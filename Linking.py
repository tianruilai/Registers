import polars as pl
import pandas as pd

df = (
    pl.scan_csv(r'C:\Users\87208\Documents\Documents\RA\Social register\dta_output\Social Registers_long_v3.csv')
    .select(['city','year','first_name','middle_names','last_name','spouse_name','spouse_last_name','college1','address'])
    .filter(pl.col("city") == "New York")
)
name_df = df.lazy()
###Step1: Separate the unique and dulicated observations
#Assign id to observations
name_df = (
    name_df
    .sort(["last_name","first_name"])
    .with_columns(pl.col("middle_names").str.slice(0, 1).alias("middle_initial"))
    .with_columns(pl.col("first_name").cumcount().alias("id"))
    .with_columns(pl.col("year").cast(pl.Int64))
    .drop("middle_names")
)

group_df = (
    name_df
    .group_by(["first_name", "last_name"])
    .agg(
        group_id=pl.col("first_name") + pl.col("last_name").alias("full_name")
    )
    .select(["last_name","first_name"])
    .with_columns(pl.col("first_name").cumcount().alias("group_id"))
)

#Assign id to groups
grouped_df = name_df.join(group_df, on=["first_name", "last_name"], how="left")
grouped_df = grouped_df.with_columns(pl.col("group_id").count().over(["group_id","year"]).suffix("_dupl"))

unique_df = grouped_df.filter(pl.col("group_id_dupl") <= 1)
duplicate_df =grouped_df.filter(pl.col("group_id_dupl") > 1).with_columns(pl.lit(1).alias("match"))

####Step2: Expand the unique dataset into a panel
years_df = (
    pl.LazyFrame({
        "year": list(range(1899, 1959))
    })
    .with_columns(
        pl.col("year").cast(pl.Int64)
    )
)
expanded_df = group_df.join(years_df,on="year",how="cross")
panel_df = expanded_df.join(unique_df,on=["first_name", "last_name", "year"],how="left").drop(["group_id_right","group_id_dupl"])

#out_df = panel_df.collect()
#print(out_df.columns)

def single_match(main_df,unmatched_df):
    middleinitial_df = (
        main_df
        .filter(pl.col("middle_initial").is_not_null())
        .group_by("group_id")
        .agg(
            pl.col("middle_initial").alias("middleinitial_list")
        )
    )
    formatch_df= (
        main_df.join(middleinitial_df, on="group_id", how="left")
        .filter(pl.col("id").is_null())
        .explode("middleinitial_list")
        .select(["year","first_name","last_name","group_id","id","middleinitial_list"])
        .rename({"middleinitial_list": "middle_initial"})
     )
    unmatched_df = (
        unmatched_df
        .filter(pl.count("middle_initial").over(["middle_initial","group_id","year"]) == 1)
    )
    matched_df = (
        formatch_df.join(unmatched_df, on=["year", "group_id", "middle_initial"], how="left")
        .filter(pl.col("match") == 1)
        .with_columns(pl.col("middle_initial").alias("characteristic"))
        .select(['city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address','group_id','id'])
    )
    main_df = main_df.select(['city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address','group_id','id'])
    main_df = pl.concat([main_df, matched_df])
    unmatched_df = (
        unmatched_df
        .join(matched_df, on=["id"], how="anti")
        .select(['match','city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address', 'group_id', 'id'])
    )
    #Step2
    spouselast_df = (
        main_df
        .filter(pl.col("spouse_last_name").is_not_null())
        .group_by("group_id")
        .agg(
            pl.col("spouse_last_name").alias("spouselast_list")
        )
    )
    formatch_df2= (
        main_df.join(spouselast_df, on="group_id", how="left")
        .filter(pl.col("id").is_null())
        .explode("spouselast_list")
        .select(["year","first_name","last_name","group_id","id","spouselast_list"])
        .rename({"spouselast_list": "spouse_last_name"})
     )
    unmatched_df2 = (
        unmatched_df
        .filter(pl.count("spouse_last_name").over(["spouse_last_name","group_id","year"]) == 1)
    )
    matched_df2 = (
        formatch_df2.join(unmatched_df2, on=["year", "group_id", "spouse_last_name"], how="left")
        .filter(pl.col("match") == 1)
        .with_columns(pl.col("spouse_last_name").alias("characteristic"))
        .select(['city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address','group_id','id'])
    )
    main_df = main_df.select(['city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address','group_id','id'])
    main_df = pl.concat([main_df, matched_df2])
    unmatched_df2 = (
        unmatched_df2
        .join(matched_df, on=["id"], how="anti")
        .select(['match','city', 'year', 'first_name', 'middle_initial', 'last_name', 'spouse_name', 'spouse_last_name', 'college1', 'address', 'group_id', 'id'])
    )


    return main_df.collect(), unmatched_df.collect(),matched_df.collect(),unmatched_df2.collect(),matched_df2.collect(),
'''
def firstround_match(main_df, duplicate_df):
    matched_step1_middlname, main_step1, unmatched_step1 =single_match(main_df, duplicate_df, "middle_initial")
    #print("step1 done")
    matched_step2_spouselast, main_step2, unmatched_step2 = single_match(main_step1.lazy(), unmatched_step1.lazy(),"spouse_last_name")
    print("step2 done")
    matched_step3_spousefirst, main_step3, unmatched_step3 = single_match(main_step2.lazy(), unmatched_step2.lazy(), "spouse_name")
    matched_step4_college, main_step4, unmatched_step4 = single_match(main_step3.lazy(), unmatched_step3.lazy(), "college1")
    matched_step5_address, main_step5, unmatched_step5 = single_match(main_step4.lazy(), unmatched_step4.lazy(), "address")

    return matched_step1_middlname, matched_step2_spouselast, matched_step3_spousefirst,\
           matched_step4_college, matched_step5_address, main_step5
'''
main, unmatched1, matched1, unmatched2, matched2 = single_match(panel_df, duplicate_df)
matched = pl.concat([matched1, matched2])

####Step3:Do the matches for duplicated observations







