import psycopg2

#conectar
conn = psycopg2.connect(host= "localhost", dbname="postgres", user="postgres", password="090407", port="5432")

cur = conn.cursor()

#...

conn.commit()

cur.close()
conn.close()
