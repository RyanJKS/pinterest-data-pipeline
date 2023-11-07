# Databricks notebook source
###################################################### MILESTONE 7: BATCH PROCESSING: SPARK ON DATABRICKS - PART 2 ##############################################################

# COMMAND ----------

# Access the cleaned dataframes using global temp views previously defined in "data_cleaning" notebook
df_pin_cleaned = spark.read.table("global_temp.df_pin_temp_view")
df_geo_cleaned = spark.read.table("global_temp.df_geo_temp_view")
df_user_cleaned = spark.read.table("global_temp.df_user_temp_view")

# COMMAND ----------

# Task 4: Find the most popular category in each country

# COMMAND ----------

# Find the most popular Pinterest category people post to based on their country.
task4_query =   """
                WITH CountCategory AS (
                    SELECT
                        geo.country,
                        pin.category,
                        COUNT(*) as category_count
                    FROM global_temp.df_geo_temp_view AS geo
                    JOIN global_temp.df_pin_temp_view AS pin 
                        ON geo.ind = pin.ind
                    GROUP BY 
                        geo.country, pin.category
                ),
                MaxCategoryCount AS (
                    SELECT
                        country,
                        MAX(category_count) as max_category_count
                    FROM CountCategory
                    GROUP BY country
                )

                SELECT
                    cc.country,
                    cc.category,
                    cc.category_count
                FROM CountCategory AS cc
                JOIN MaxCategoryCount AS mcc
                    ON cc.country = mcc.country
                    AND cc.category_count = mcc.max_category_count
                ORDER BY 
                    country, category_count DESC;
                """
display(spark.sql(task4_query))

# COMMAND ----------

# Task 5: Find which was the most popular category each year

# COMMAND ----------

# Find how many posts each category had between 2018 and 2022.
task5_query =   """
                SELECT
                    YEAR(geo.timestamp) AS post_year,
                    pin.category,
                    COUNT(*) AS category_count
                FROM global_temp.df_geo_temp_view AS geo
                JOIN global_temp.df_pin_temp_view AS pin
                    ON geo.ind = pin.ind
                WHERE
                    YEAR(geo.timestamp) BETWEEN 2018 AND 2022
                GROUP BY
                    YEAR(geo.timestamp), pin.category
                ORDER BY
                    post_year DESC, category_count DESC;
                """
display(spark.sql(task5_query))

# COMMAND ----------

# Task 6: Find the user with most followers in each country

# COMMAND ----------

# Part 1: For each country find the user with the most followers.
task6_part1_query = """
                    WITH RankedUsers AS (
                        SELECT
                            g.country,
                            p.poster_name,
                            p.follower_count,
                            RANK() OVER (PARTITION BY g.country ORDER BY p.follower_count DESC) as rank
                        FROM global_temp.df_geo_temp_view g
                        JOIN global_temp.df_pin_temp_view p ON g.ind = p.ind
                    )

                    SELECT
                        country,
                        poster_name,
                        follower_count
                    FROM RankedUsers
                    WHERE rank = 1
                    ORDER BY country, poster_name
                    """
display(spark.sql(task6_part1_query))

# Part 2: Based on the above query, find the country with the user with most followers.
task6_part2_query= f"""
                    SELECT
                        country,
                        follower_count
                    FROM ({task6_part1_query})
                    ORDER BY 
                        follower_count DESC
                    LIMIT 1;
                    """
display(spark.sql(task6_part2_query))

# COMMAND ----------

# Task 7: Find the most popular category for different age groups

# COMMAND ----------

task7_query =   """
                WITH AgeGroupCategories AS (
                    SELECT
                        CASE
                            WHEN users.age >= 18 AND users.age <= 24 THEN '18-24'
                            WHEN users.age >= 25 AND users.age <= 35 THEN '25-35'
                            WHEN users.age >= 36 AND users.age <= 50 THEN '36-50'
                            WHEN users.age > 50 THEN '50+'
                        END AS age_group,
                        pin.category
                    FROM global_temp.df_user_temp_view AS users
                    JOIN global_temp.df_pin_temp_view AS pin 
                        ON users.ind = pin.ind
                ),
                CategoryCounts AS (
                    SELECT
                        age_group,
                        category,
                        COUNT(*) AS category_count
                    FROM AgeGroupCategories
                    GROUP BY age_group, category
                ),
                RankedCategories AS (
                    SELECT
                        age_group,
                        category,
                        category_count,
                        RANK() OVER (PARTITION BY age_group ORDER BY category_count DESC) as category_rank
                    FROM CategoryCounts
                )
                SELECT
                    age_group,
                    category,
                    category_count
                FROM RankedCategories
                WHERE category_rank = 1
                ORDER BY age_group;
                """
display(spark.sql(task7_query))

# COMMAND ----------

# Task 8: Find the median follower count for different age groups

# COMMAND ----------

task8_query =   """
                WITH AgeGroupCategories AS (
                    SELECT
                        CASE
                            WHEN users.age >= 18 AND users.age <= 24 THEN '18-24'
                            WHEN users.age >= 25 AND users.age <= 35 THEN '25-35'
                            WHEN users.age >= 36 AND users.age <= 50 THEN '36-50'
                            WHEN users.age > 50 THEN '50+'
                        END AS age_group,
                        pin.follower_count
                    FROM global_temp.df_user_temp_view AS users
                    JOIN global_temp.df_pin_temp_view AS pin 
                        ON users.ind = pin.ind
                )
                SELECT
                    age_group,
                    percentile_approx(follower_count, 0.5) AS median_follower_count
                FROM AgeGroupCategories
                GROUP BY age_group
                ORDER BY age_group;
                    """
display(spark.sql(task8_query))

# COMMAND ----------

# Task 9: Find how many users have joined each year?

# COMMAND ----------

# Find how many users have joined between 2015 and 2020.
task9_query="""
            SELECT
                YEAR(date_joined) AS post_year,
                COUNT(*) AS number_users_joined
            FROM global_temp.df_user_temp_view
            WHERE 
                YEAR(date_joined) BETWEEN 2015 AND 2020
            GROUP BY
                YEAR(date_joined)
            ORDER BY
                post_year DESC;
            """
display(spark.sql(task9_query))

# COMMAND ----------

# Task 10: Find the median follwoer count of users based on thei joining year

# COMMAND ----------

# Find the median follower count of users have joined between 2015 and 2020.
task10_query =  """
                SELECT
                    YEAR(users.date_joined) AS post_year,
                    percentile_approx(pin.follower_count, 0.5) AS median_follower_count
                FROM global_temp.df_user_temp_view AS users
                JOIN global_temp.df_pin_temp_view AS pin
                    ON users.ind = pin.ind
                WHERE
                    YEAR(users.date_joined) BETWEEN 2015 AND 2020
                GROUP BY
                    YEAR(users.date_joined)
                """
display(spark.sql(task10_query))

# COMMAND ----------

# Task 11: Find the median follower count of users based on their joining year and age group

# COMMAND ----------

# Find the median follower count of users that have joined between 2015 and 2020, based on which age group they are part of.
task11_query =  """
                SELECT
                    CASE
                        WHEN users.age >= 18 AND users.age <= 24 THEN '18-24'
                        WHEN users.age >= 25 AND users.age <= 35 THEN '25-35'
                        WHEN users.age >= 36 AND users.age <= 50 THEN '36-50'
                        WHEN users.age > 50 THEN '50+'
                    END AS age_group,
                    YEAR(users.date_joined) AS post_year,
                    percentile_approx(pin.follower_count, 0.5) AS median_follower_count
                FROM global_temp.df_user_temp_view AS users
                JOIN global_temp.df_pin_temp_view AS pin 
                    ON users.ind = pin.ind
                WHERE
                    YEAR(users.date_joined) BETWEEN 2015 AND 2020
                GROUP BY
                    age_group, post_year
                ORDER BY
                    age_group, post_year DESC;
                """
display(spark.sql(task11_query))

# COMMAND ----------


