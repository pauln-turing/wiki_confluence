Database seeding information for a Confluence Enterprise Wiki, Saad Team

The files and folder structure are as follows:
- **`generated_data`**: The folder with the seeding tables for the project;
- **`gemini.py`**: The faker seeder file. Creates a `generated_data` folder and adds all table data inside it. Generated with gemini 2.5pro, in several interactions.
- **`verify_all.py`**: Verifies that all relations that are tightly addigned are correct, like if an approved item is correcly listed in all related tables.
- **`verify_approvals.py`**: Checks only if approvals are correctly related in the linked tables. `verify_all.py` derived from this idea but is more complete.
- **`verify_seed.py`**: Certifies all rows that have foreign keys actually point to an existing foreign key.

**Note:** All python scripts must be executed from a folder that contains the `generated_data` folder with all seeded files and a file named `schema.dbml`. This file must have the database schema from the `database.io` website. Just copy the text from the schema in the website's raw format. The scripts use this schema to check integrity.
