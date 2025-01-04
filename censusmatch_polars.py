import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from nltk.metrics.distance import jaro_winkler_similarity
from pathlib import Path
from typing import Optional, Sequence
import time
from . import codebooks

#Set the directory
census_dir = Path('/homes/data/census-ipums/current/csv')
cache_dir = Path.home() / 'bulk' / 'cache'

#Hash the name
hash_last_name = pl.col('namelast').str.slice(offset=0, length=2).hash().alias('lname_top2_hash')
hash_first_name = (
    pl.col('namefrst')
    .str.slice(offset=0, length=1)
    .map_dict({chr(c): c for c in range(255)}, default=0)
    .alias('fname_top1_char')
)

extract_initials = (
    pl.col('namefrst')
    .str.split(by=' ')
    .list.eval(
        pl.element()
        .str.slice(offset=0, length=1)
    )
    .list.slice(offset=0, length=2)
    .list.join('')
    .alias('fname_initials')
)

first_name_only = (
    pl.col('namefrst')
    .str.splitn(' ', n=2)
    .struct.field('field_0')
    .alias('first_name_only')
)

class CensusMatcher(object):
    #years_to_load should be a sequence of integers. The default value range(1900, 1941, 10) is indeed a sequence of integers
    def __init__(self, years_to_load: Sequence[int] = range(1900, 1941, 10)) -> None:
        print('Loading census files...')

        cache_dir.mkdir(exist_ok=True)

        self.census_years = years_to_load
        self.censuses = {}
        for year in tqdm(list(years_to_load)):
            self.censuses[year] = self.load_census(year, filter_male=True)
            print(f'Done with {year}')

        self.census_combined = (
            pl.concat(self.censuses.values())
            .with_columns(pl.col('census_year').cast(pl.Int64))
        )
        
    
    def load_census(self, year: int, vars: Optional[Sequence[str]] = None, filter_male: bool = True) -> pl.LazyFrame:
        if (cache_dir / f"{year}.parquet").exists():
            print(f'Using cache for {year}')
            return pl.scan_parquet(cache_dir / f"{year}.parquet")

        df = (
            pl.scan_csv(census_dir / f"{year}.csv")
            .select([
                'namefrst',
                'namelast',
                'bpl',
                'age',
                'sex',
                'race',
                'statefip',
                'histid',
                'occ1950'
            ])
            .with_columns(
                hash_last_name,
                hash_first_name,
                extract_initials,
                first_name_only
            )
            .with_columns(
                pl.lit(year).alias('census_year')
            )
        )

        print(df.columns)

        if filter_male:
            df = df.filter(pl.col('sex') == 1)
        
        df_collected = df.collect()
        print(f'Writing {year} to cache')
        df_collected.write_parquet(cache_dir / f"{year}.parquet")
    
        return df_collected.lazy()
    
    def prep_input_df(self, df: pl.LazyFrame, bpl_col: str, fname_col: str, lname_col: str) -> pl.LazyFrame:
        df_prepped = (
            df
            .filter(pl.col('exec_id').is_not_null())
            
            .join(
                (
                    codebooks.bpl_codebook.lazy()
                    .rename({'label': bpl_col, 'code': 'bpl_code'})
                    .select([bpl_col, 'bpl_code'])
                    .with_columns(pl.col(bpl_col).str.to_uppercase().str.strip())
                ),
                how='left',
                on=bpl_col,
                validate='m:1'
            )
            .with_columns(
                pl.col(lname_col).str.to_uppercase().str.strip().alias('namelast'),
                pl.col(fname_col).str.to_uppercase().str.strip().alias('namefrst')
            )
            .with_columns(
                hash_last_name,
                hash_first_name,
                extract_initials,
                first_name_only
            )
            .sort('year')
            .join_asof(
                pl.DataFrame(
                    {'census_year': self.census_years}
                ).lazy().sort('census_year'),
                left_on=pl.col('year'),
                right_on=pl.col('census_year'),
                strategy='backward'
            )
            .with_columns(
                pl.col(bpl_col).str.to_uppercase().str.strip(),
                pl.col('bpl_code').cast(pl.Int64),
                (pl.col('census_year') - pl.col('year_of_birth')).alias('age')
            )
            .with_columns(
                pl.struct([
                    'record_id', 
                    'census_year', 
                    'namefrst', 
                    'namelast', 
                    'lname_top2_hash', 
                    'fname_top1_char', 
                    'fname_initials',
                    'first_name_only',
                    'bpl_code', 
                    'age'
                ]).alias('bundle_for_matching')
            )
        )

        return df_prepped
    
    def narrow_down_blocking(self, census_blocked, rec_struct, return_code):
        census_blocked_ln = census_blocked.filter(
            pl.col('namelast') == rec_struct['namelast'] 
        )

        if census_blocked_ln.height == 1:
            return {
                'method': return_code,
                'histid': census_blocked_ln.item(row=0, column='histid'),
                'census_namefrst': census_blocked_ln.item(row=0, column='namefrst'),
                'census_namelast': census_blocked_ln.item(row=0, column='namelast')
            }

        census_blocked_age = census_blocked_ln.filter(
            (pl.col('age') - rec_struct['age']).abs() <= 1
        )

        if census_blocked_age.height == 1:
            return {
                'method': return_code,
                'histid': census_blocked_age.item(row=0, column='histid'),
                'census_namefrst': census_blocked_age.item(row=0, column='namefrst'),
                'census_namelast': census_blocked_age.item(row=0, column='namelast')
            }
        
        census_blocked_fn = census_blocked_age.filter(
            pl.col('namefrst').str.slice(offset=0, length=4) == rec_struct['namefrst'][:5]
        )

        if census_blocked_fn.height == 1:
            return {
                'method': return_code,
                'histid': census_blocked_fn.item(row=0, column='histid'),
                'census_namefrst': census_blocked_fn.item(row=0, column='namefrst'),
                'census_namelast': census_blocked_fn.item(row=0, column='namelast')
            }

        if census_blocked_fn.height > 1:
            return 'overlength'
        else:
            return 'norec'
 
    def merge_to_census_parallel(self, df: pl.LazyFrame, bpl_col: str, fname_col: str, lname_col: str) -> pl.DataFrame:
        df = self.prep_input_df(df, bpl_col, fname_col, lname_col).rename({'bpl_code': 'bpl'})

        df_step1 = (
            df
            .join(
                (
                    self.census_combined
                    .rename({'age': 'census_age'})
                    .select(['census_age', 'census_year', 'namelast', 'first_name_only', 'fname_initials', 'bpl', 'histid', 'namefrst', 'occ1950'])
                    .rename({'namefrst': 'census_namefrst'})
                ),
                how='left',
                on=[
                    'census_year',
                    'namelast',
                    'first_name_only',
                    'fname_initials',
                    'bpl'
                ]
            )
            .filter(
                pl.col('census_age').is_null() |
                ((pl.col('age') - pl.col('census_age')).abs() <= 3)
            )
            .with_columns(
                pl.col('namelast').alias('census_namelast'),
            )
            .cache()
        )


        df_step1_matched   = (
            df_step1.filter(pl.col('histid').is_not_null()).with_columns(pl.lit('perfect').alias('method'))
            .with_columns(
                (pl.col('age') - pl.col('census_age'))
                .pow(2)
                .add((pl.col('occ1950').fill_null(0) != pl.lit(290)).cast(pl.Int64).mul(0.5))
                .alias('score')
            )
            .with_columns(
                pl.col('score').min().over('record_id').alias('min_rec_score')
            )
            .filter(
                pl.col('score') <= pl.when(pl.col('min_rec_score') < 1).then(
                    pl.lit(1)
                ).otherwise(
                    pl.col('min_rec_score')
                )
            )
            .select(['record_id', 'histid', 'year', 'census_year', 'last_name', 'first_middle_name', 'namelast', 'namefrst', 'method', 'census_age', 'age', 'census_namelast', 'census_namefrst'])
        )

        # print(f'len of match round 1 is {df_step1_matched.height}')

        df_step1_unmatched = df_step1.filter(pl.col('histid').is_null()).drop(['histid', 'census_age', 'census_namelast', 'census_namefrst', 'occ1950'])

        df_step2 = (
            df_step1_unmatched
            .join(
                (
                    self.census_combined
                    .rename({'age': 'census_age'})
                    .select(['census_age', 'census_year', 'namelast', 'fname_initials', 'bpl', 'histid', 'namefrst', 'occ1950'])
                    .rename({'namefrst': 'census_namefrst'})
                ),
                how='left',
                on=[
                    'census_year',
                    'namelast',
                    'fname_initials',
                    'bpl'
                ]
            )
            .filter(
                pl.col('histid').is_null() |
                (
                    ((pl.col('age') - pl.col('census_age')).abs() <= 5) &
                    (pl.col('fname_initials').str.lengths() >= 2)
                )
            )
            .with_columns(
                pl.col('namelast').alias('census_namelast'),
            )
            .cache()
        )

        df_step2_matched   = (
            df_step2.filter(pl.col('histid').is_not_null()).with_columns(pl.lit('initials_match').alias('method'))
            .with_columns(
                (pl.col('age') - pl.col('census_age'))
                .pow(2)
                .add((pl.col('occ1950').fill_null(0) != pl.lit(290)).cast(pl.Int64).mul(0.5))
                .alias('score')
            )
            .with_columns(
                pl.col('score').min().over('record_id').alias('min_rec_score')
            )
            .filter(
                pl.col('score') <= pl.when(pl.col('min_rec_score') < 1).then(
                    pl.lit(1)
                ).otherwise(
                    pl.col('min_rec_score')
                )
            )
            .select(['record_id', 'histid', 'year', 'census_year', 'last_name', 'first_middle_name', 'namelast', 'namefrst', 'method', 'census_age', 'age', 'census_namelast', 'census_namefrst'])
        )

        # print(f'len of match round 2 is {df_step2_matched.height}')


        df_step2_unmatched = df_step2.filter(pl.col('histid').is_null()).drop(['histid', 'census_age', 'census_namelast', 'census_namefrst', 'occ1950'])

        df_step3 = (
            df_step2_unmatched
            .join(
                (
                    self.census_combined
                    .rename({'age': 'census_age'})
                    .select(['census_age', 'census_year', 'namelast', 'first_name_only', 'bpl', 'histid', 'namefrst', 'occ1950'])
                    .rename({'namefrst': 'census_namefrst'})
                ),
                how='left',
                on=[
                    'census_year',
                    'namelast',
                    'first_name_only',
                    'bpl'
                ]
            )
            .filter(
                pl.col('census_age').is_null() |
                ((pl.col('age') - pl.col('census_age')).abs() <= 5)
            )
            .with_columns(
                pl.col('namelast').alias('census_namelast'),
            )
            .cache()
        )

        df_step3_matched   = (
            df_step3.with_columns(pl.lit('fname_match').alias('method')).filter(pl.col('histid').is_not_null())
            .with_columns(
                (pl.col('age') - pl.col('census_age'))
                .pow(2)
                .add((pl.col('occ1950').fill_null(0) != pl.lit(290)).cast(pl.Int64).mul(0.5))
                .alias('score')
            )
            .with_columns(
                pl.col('score').min().over('record_id').alias('min_rec_score')
            )
            .filter(
                pl.col('score') <= pl.when(pl.col('min_rec_score') < 1).then(
                    pl.lit(1)
                ).otherwise(
                    pl.col('min_rec_score')
                )
            )
            .select(['record_id', 'histid', 'year', 'census_year', 'last_name', 'first_middle_name', 'namelast', 'namefrst', 'method', 'census_age', 'age', 'census_namelast', 'census_namefrst'])
        )

        # print(f'len of match round 3 is {df_step3_matched.height}')

        df_step3_unmatched = (
            df_step3
            .with_columns(
                pl.lit('unmatched').alias('method'), 
            )
            .filter(pl.col('histid').is_null())
        )

        # print(f'len of unmatched is {df_step3_unmatched.height}')

        out_df = pl.concat(
            [
                df_step1_matched,
                df_step2_matched,
                df_step3_matched,
                df_step3_unmatched.select(['record_id', 'histid', 'year', 'census_year', 'last_name', 'first_middle_name', 'namelast', 'namefrst', 'method', 'census_age', 'age', 'census_namelast', 'census_namefrst'])
            ]
        )

        return out_df.collect()



