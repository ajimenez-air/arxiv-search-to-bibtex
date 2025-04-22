import arxiv
import re

def format_query(raw_query: str) -> str:
    """
    Tomar una cadena como:
    (
      ("Term1" OR "Term2" ...)
      AND
      ("TermA" OR ...)
    )
    y devolver:
      (all:"Term1" OR all:"Term2" ...) AND (all:"TermA" OR ...)
    """
    single = ' '.join(raw_query.strip().split())
    formatted = re.sub(r'"([^"]+)"', r'all:"\1"', single)
    return formatted

def result_to_bibtex(result) -> str:
    aid = result.entry_id.split('/')[-1]
    year = result.published.year if hasattr(result.published, 'year') else result.published[:4]
    authors = ' and '.join(author.name for author in result.authors)
    title = result.title.replace('\n', ' ').strip()
    primary_cat = result.primary_category
    return f"""@article{{{aid},
  title         = {{{title}}},
  author        = {{{authors}}},
  year          = {{{year}}},
  eprint        = {{arxiv:{aid}}},
  archivePrefix = {{ArXiv}},
  primaryClass  = {{{primary_cat}}},
  url           = {{{result.entry_id}}}
}}"""

def read_query_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return None

raw_query = read_query_from_file('query.txt')
if raw_query is None:
    print("No se pudo cargar la query. El programa se detendrá.")
    exit(1)

formatted_query = format_query(raw_query)

client = arxiv.Client()

search = arxiv.Search(
    query=formatted_query,
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

output_file = 'resultados_arxiv.bib'
with open(output_file, 'w', encoding='utf-8') as bibfile:
    try:
        for result in client.results(search):
            bibfile.write(result_to_bibtex(result) + '\n\n')
    except arxiv.UnexpectedEmptyPageError as e:
        print("Se han recuperado todos los resultados disponibles")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

print(f"Se han exportado las entradas al archivo '{output_file}'. Consulta usada:")
print(formatted_query)
