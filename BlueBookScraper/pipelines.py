# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import json
import os
import configparser

import psycopg2
import shutil


def makeDictFromCSV(csvFilePath):
    rows = []
    with open(csvFilePath, 'r', newline='') as csvFile:
        csvReader = csv.DictReader(csvFile)
        for row in csvReader:
            # row['courselabel'] = row['courselabel'].replace('\r', '')
            # row['courselabel'] = row['courselabel'].replace('\n', '')
            rows.append(row)
    return(rows)

class dataBaseWriter():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        # self.conn = psycopg2.connect(host=config['localdatabase']['host'], dbname=config['localdatabase']['dbname'], user=config['localdatabase']['user'],
        #                         password=config['localdatabase']['password'], port=5432)
        self.conn = psycopg2.connect(host=config['pgdatabase']['host'], dbname=config['pgdatabase']['dbname'], user=config['pgdatabase']['user'],
                                 password=config['pgdatabase']['password'], port=5432)

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, *args):
        self.conn.commit()
        self.cur.close()
        self.conn.close()


class dataBaseEditor():

    @staticmethod
    def check_table_exists(cursor, table_name, schema_name='public'):
        query = """
               SELECT EXISTS (
                   SELECT 1 
                   FROM information_schema.tables 
                   WHERE table_schema = %s
                   AND table_name = %s
               ); """
        cursor.execute(query, (schema_name, table_name))
        table_exists = cursor.fetchone()[0]
        return table_exists

    @staticmethod
    def create_table(cursor, table_name, schema_name='public'):
        sql_create_table = f"""
                CREATE TABLE {table_name} (
                    crn INTEGER,
                    semester VARCHAR(40),
                    courseLabel VARCHAR(40),
                    instructor VARCHAR(100),
                    courseTitle VARCHAR(100),
                    insEval REAL,
                    insEvalStudentNum INTEGER,
                    crEval REAL,
                    crEvalStudentNum INTEGER,
                    enrollment INTEGER,
                    description VARCHAR(3000),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        cursor.execute(sql_create_table)

    @staticmethod
    def dump_table_rows(cursor, table_name, data):
        dump_rows = f"TRUNCATE TABLE {table_name} RESTART IDENTITY;"
        cursor.execute(dump_rows)
    @staticmethod
    def update_table(cursor, table_name, data):
        def convert_na_to_null(value):
            if value == 'n/a':
                return None
            else:
                return value

        # Process the data for NULL conversion
        processed_values = tuple(convert_na_to_null(value) for value in data.values())
        columns = ', '.join(["\"{}\"".format(col) for col in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))
        print(processed_values)
        print(columns)
        print(placeholders)


        query = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})      
                """

        # Execute the query
        cursor.execute(query, processed_values)

class dataBaseEditor2():

    @staticmethod
    def check_table_exists(cursor, table_name, schema_name='public'):
        query = """
                       SELECT EXISTS (
                           SELECT 1 
                           FROM information_schema.tables 
                           WHERE table_schema = %s
                           AND table_name = %s
                       ); """
        cursor.execute(query, (schema_name, table_name))
        table_exists = cursor.fetchone()[0]
        return table_exists

    @staticmethod
    def create_table(cursor, table_name, schema_name='public'):
        sql_create_table = f"""
        CREATE TABLE {table_name}(
            document_name TEXT NOT NULL PRIMARY KEY,
            file_data BYTEA NOT NULL
        ); """
        cursor.execute(sql_create_table)

    @staticmethod
    def store_pdf(cursor, file_path, table_name):
        not_string_literal = "'"
        not_string_literal_2 = ""
        with open(file_path, 'rb') as f:
            pdf_data = f.read()
        cursor.execute(f"INSERT INTO {table_name} (document_name, file_data) VALUES ('{os.path.split(file_path)[1].replace(not_string_literal,not_string_literal_2)}', {psycopg2.Binary(pdf_data)})")

    @staticmethod
    def store_multiple_pdfs(cursor, dir_path, table_name):
        not_string_literal = "'"
        not_string_literal_2 = ""
        query = f"INSERT INTO {table_name} (document_name, file_data) VALUES "
        for root, dirs, files in os.walk(dir_path):
            for index, file in enumerate(files):
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    pdf_data = f.read()
                query = query + f"('{os.path.split(file_path)[1].replace(not_string_literal,not_string_literal_2)}', {psycopg2.Binary(pdf_data)})"
                if index == len(files) - 1:
                    #print('exection1')
                    try:
                        # print('exection2')
                        cursor.execute(query)
                    except psycopg2.OperationalError:
                        print("SSL violation")
                        cursor.execute(query)
                    except psycopg2.errors.UniqueViolation:
                        print("Unique violation")
                        pass
                    print("Commited " + str(index + 1) + " files")
                elif (index % 1 == 0 and index != 0):
                    try:
                    #print('exection2')
                        cursor.execute(query)
                    except psycopg2.OperationalError:
                        print("SSL violation")
                        cursor.execute(query)
                    except psycopg2.errors.UniqueViolation:
                        print("Unique violation")
                        pass
                    query = f"INSERT INTO {table_name} (document_name, file_data) VALUES "
                    print("Commited " + str(index + 1) + " files")
                else:
                    #print('making ,')
                    query = query + ", "


    @staticmethod
    def retrieve_pdf(cursor, document_name, output_path, table_name):
            cursor.execute(
                f"SELECT file_data FROM {table_name} WHERE document_name = %s",
                (document_name,)
            )
            result = cursor.fetchone()
            if result:
                with open(output_path, 'wb') as f:
                    f.write(result[0])

    @staticmethod
    def dump_table_rows(cursor, table_name):
        dump_rows = f"TRUNCATE TABLE {table_name} RESTART IDENTITY;"
        cursor.execute(dump_rows)

class dataBaseHelper3():
    @staticmethod
    def compare_stuff(cursor, table_name, csvfile):
        with open(csvfile, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                query = f"""UPDATE {table_name}
                            SET description = '{row[2].strip().replace("'","")}'
                            WHERE courselabel = '{row[1]}';
                        """
                cursor.execute(query)


def runForCoursestable():
    listOfDicts = makeDictFromCSV("test2.csv")

    print(listOfDicts)
    with dataBaseWriter() as db_writer:
        if not dataBaseEditor.check_table_exists(db_writer, 'courses'):
            dataBaseEditor.create_table(db_writer, 'courses')
            for dictionary in listOfDicts:
                dataBaseEditor.update_table(db_writer, 'courses', dictionary)
        else:
            dataBaseEditor.dump_table_rows(db_writer, 'courses', listOfDicts)
            for dictionary in listOfDicts:
                dataBaseEditor.update_table(db_writer, 'courses', dictionary)

def runForDocuments():
    table_name = 'documents'
    dir_path = 'syllabi'

    with dataBaseWriter() as db_writer:
        if not dataBaseEditor2.check_table_exists(db_writer, table_name):
             dataBaseEditor2.create_table(db_writer, table_name)
    print('tables checked')
    for root, dirs, files in os.walk(dir_path):
        for index, file in enumerate(files):
            try:
                with dataBaseWriter() as db_writer:
                    print(os.path.join(root, file))
                    dataBaseEditor2.store_pdf(db_writer, os.path.join(root, file), table_name)
                    print("Commited " + str(index + 1) + " files")
                    shutil.move(os.path.join(root, file), 'usedSyllabi')
            except psycopg2.OperationalError:
                print("SSL violation")
                print(os.path.join(root, file))


                # with open(file_path, 'rb') as f:
                #     pdf_data = f.read()
                # cursor.execute(
                #     f"INSERT INTO {table_name} (document_name, file_data) VALUES ('{os.path.split(file_path)[1].replace("'", "")}', {psycopg2.Binary(pdf_data)})")


    # with dataBaseWriter() as db_writer:
    #     #dataBaseEditor2.dump_table_rows(db_writer, 'documents')
    #     #dataBaseEditor2.retrieve_pdf(db_writer, 'Kohler,_Janelle_Marie;35238;PSY_2073.006;Statistics_for_Psychology;Spr_2024;pdf.pdf', 'outs/file1.pdf', table_name)
    #     if not dataBaseEditor2.check_table_exists(db_writer, table_name):
    #         dataBaseEditor2.create_table(db_writer, table_name)
    #         dataBaseEditor2.store_multiple_pdfs(db_writer, 'syllabi', 'documents')
    #     else:
    #         dataBaseEditor2.store_multiple_pdfs(db_writer, 'syllabi', 'documents')

#
# if __name__ == '__main__':
#     with dataBaseWriter() as db_writer:
#         dataBaseHelper3.compare_stuff(db_writer, "courses", "test1.csv")
#     # runForDocuments()
#     # with dataBaseWriter() as db_writer:
#     #     dataBaseEditor2.retrieve_pdf(db_writer, 'Kohler,_Janelle_Marie;35238;PSY_2073.006;Statistics_for_Psychology;Spr_2024;pdf.pdf', 'outs/file2.pdf', 'documents')

class BluebookscraperPipeline:
    def process_item(self, item, spider):
        return item

class saveToDBPipeline:
    def process_item(self, item, spider):
        with dataBaseWriter() as db_writer:
            if not dataBaseEditor.check_table_exists(db_writer, 'courses'):
                dataBaseEditor.create_table(db_writer, 'courses')
                dataBaseEditor.update_table(db_writer, 'courses', item)
            else:
                dataBaseEditor.dump_table_rows(db_writer, 'courses', item)
                dataBaseEditor.update_table(db_writer, 'courses', item)
