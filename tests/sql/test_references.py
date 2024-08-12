from pycodehash.sql.references import extract_table_references


def test_enriched_table_reference_visitor_cte():
    query = """CREATE TABLE output_table AS (
        WITH intermediate_table AS (
            SELECT
                *
            FROM sdb.source_table1 AS st1
            LEFT JOIN sdb.source_table2 AS st2 ON st1.record_id = st2.record_id
            LEFT JOIN sdb.source_table3 AS st3 ON st1.record_id = st3.record_id
        ),
        another_intermediate_table AS (
            SELECT * FROM hello_world
        ),

        SELECT
            *
        FROM
            intermediate_table
    )
    """
    input_tables, output_tables, dropped_tables = extract_table_references(
        query, dialect="sparksql", default_db="hello_world"
    )

    assert input_tables == {"sdb.source_table3", "sdb.source_table2", "hello_world.hello_world", "sdb.source_table1"}
    assert output_tables == {"hello_world.output_table"}
    assert dropped_tables == set()
