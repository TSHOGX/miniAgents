# Schema Generator

A simple database schema generator that extracts schema information from databases and formats it in a human-readable format.

## Output Format

```
[DB_ID] {db_name}
[Schema]
# Table: vhr_x0_charge
[
(car_id: INT, the id of cars, Examples: [67897654389, 09196984381, 31121984321]),
(start_soh: INT, the start soh of charge, Examples: [10, 22, 89]),
(ave_curr: FLOAT, average current of charging period, Examples: [102.2, 232, 80.99])
]
# Table: {table_name}
[
({column_name}: {data_type}, {column_description}, Examples: {examples})
]
```

## Example

See `example.py` for complete examples of connecting to different database types. 