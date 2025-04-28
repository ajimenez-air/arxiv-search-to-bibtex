import arxiv
import re
from typing import List, Set, Tuple, Dict

def format_query(raw_query: str) -> str:
    """
    Tomar una cadena como:
    (("Term1" OR "Term2" ...) AND ("TermA" OR ...))
    y devolver:
    (abs:"Term1" OR abs:"Term2"...) AND (abs:"TermA" OR...)
    """
    query = re.sub(r'"([^"]+)"', r'abs:"\1"', raw_query)
    
    # Eliminar espacios innecesarios
    query = re.sub(r'\s+', ' ', query)  # Convertir múltiples espacios en uno solo
    query = re.sub(r'\(\s+', '(', query)  # Eliminar espacios después de paréntesis de apertura
    query = re.sub(r'\s+\)', ')', query)  # Eliminar espacios antes de paréntesis de cierre
    query = re.sub(r'\s+(AND|OR)\s+', r' \1 ', query)  # Mantener un espacio alrededor de operadores
    
    return query.strip()

def extract_keywords_from_query(raw_query: str) -> Dict[str, Set[str]]:
    """
    Extrae las palabras clave de la consulta separadas en dos grupos
    """
    # Definir los dos grupos de palabras clave
    grupo1_keywords = [
        # Primera parte (prompting/agents/RAG)
        "Prompting", "Prompt design", "Prompt optimization", "Prompting techniques",
        "LLM agents", "AI agents", "Autonomous language agents", "Intelligent agents", 
        "Agentic", "Multi-agent systems", "Retrieval-Augmented Generation",
        "RAG", "retrieval-enhanced generation", "Automatic", "Automated", "Machine-assisted", 
        "AI-based", "Computational"
    ]
    
    grupo2_keywords = [
        # Segunda parte (simplificación/accesibilidad)
        "Text Simplification", "Automatic text simplification", "Text rewriting", 
        "Linguistic simplification", "ATS", "Plain language", "Clear language",
        "Easy-to-read", "Easy Read", "Lectura Fácil", "Text accessibility",
        "Accessible language", "Cognitive accessibility", "Readability", 
        "Readability standards", "Text clarity", "Simplification guidelines", 
        "Language Simplification Standards", "Plain Language Regulation",
        "Public sector", "Public administration", "Government sector", 
        "Governmental institutions", "Public documents", "Administration documents", 
        "Administrative texts", "Official documents", "Bureaucratic texts",
        "Legal documents", "Regulatory texts", "Legal texts", "Normative documents", 
        "Legislative documents", "Simplification dataset", "Text simplification corpus", 
        "Simplified corpus", "Simplified datasets", "Simplification corpus",
        "Open dataset", "Public dataset", "Available dataset", "Freely available corpus", 
        "Simple-complex word pairs", "Plain language", "Clear language", "Readability", 
        "Text clarity", "Easy-to-read", "Easy Read", "Lectura Fácil",
        "Text accessibility", "Cognitive accessibility", "Accessible language"
    ]
    
    # Convertir a minúsculas y eliminar duplicados
    grupo1 = {keyword.lower() for keyword in grupo1_keywords}
    grupo2 = {keyword.lower() for keyword in grupo2_keywords}
    
    # Devolver los dos grupos como un diccionario
    return {
        "grupo1": grupo1,
        "grupo2": grupo2,
        "todos": grupo1.union(grupo2)
    }

def find_matching_keywords_by_group(text: str, keywords_dict: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """
    Encuentra qué palabras clave aparecen en el texto dado, separadas por grupo
    """
    text_lower = text.lower()
    
    # Buscar palabras clave de cada grupo
    grupo1_matches = [keyword for keyword in keywords_dict["grupo1"] if keyword in text_lower]
    grupo2_matches = [keyword for keyword in keywords_dict["grupo2"] if keyword in text_lower]
    
    return {
        "grupo1": grupo1_matches,
        "grupo2": grupo2_matches,
        "todos": grupo1_matches + grupo2_matches
    }

def result_to_bibtex(result, keywords_dict: Dict[str, Set[str]]) -> str:
    aid = result.entry_id.split('/')[-1]
    year = result.published.year if hasattr(result.published, 'year') else result.published[:4]
    authors = ' and '.join(author.name for author in result.authors)
    title = result.title.replace('\n', ' ').strip()
    abstract = result.summary.replace('\n', ' ').strip()
    primary_cat = result.primary_category
    
    # Encuentra las palabras clave que aparecen en el abstract
    matching_keywords = find_matching_keywords_by_group(abstract, keywords_dict)
    keywords_comment = f"% Keywords found: {', '.join(matching_keywords['todos'])}"
    
    return f"""{keywords_comment}
@article{{{aid},
  title         = {{{title}}},
  author        = {{{authors}}},
  year          = {{{year}}},
  abstract      = {{{abstract}}},
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

def extract_terms_from_query(query_text):
    """
    Extrae todos los términos entre comillas del texto de consulta
    """
    pattern = r'"([^"]+)"'
    return re.findall(pattern, query_text)

raw_query = read_query_from_file('query.txt')
if raw_query is None:
    print("No se pudo cargar la query. El programa se detendrá.")
    exit(1)

# Extraer los términos de la consulta para actualizar dinámicamente los grupos
query_terms = extract_terms_from_query(raw_query)

formatted_query = format_query(raw_query)
keywords_dict = extract_keywords_from_query(raw_query)

client = arxiv.Client()

search = arxiv.Search(
    query=formatted_query,
    max_results=500,
    sort_by=arxiv.SortCriterion.Relevance,
    sort_order=arxiv.SortOrder.Descending
)

output_file = 'resultados_arxiv.bib'
with open(output_file, 'w', encoding='utf-8') as bibfile:
    try:
        count = 0
        filtered_by_year = 0
        filtered_by_keywords = 0
        
        for result in client.results(search):
            # Obtener el año de publicación
            year = result.published.year if hasattr(result.published, 'year') else int(result.published[:4])
            
            # Paso 1: Filtrar por año
            if year <= 2017:
                filtered_by_year += 1
                continue
                
            # Paso 2: Verificar si el abstract contiene palabras clave de ambos grupos
            abstract = result.summary.replace('\n', ' ').strip()
            matching_keywords = find_matching_keywords_by_group(abstract, keywords_dict)
            
            # Solo incluir si tiene al menos una palabra clave de cada grupo
            if len(matching_keywords["grupo1"]) >= 1 and len(matching_keywords["grupo2"]) >= 1:
                bibfile.write(result_to_bibtex(result, keywords_dict) + '\n\n')
                count += 1
            else:
                filtered_by_keywords += 1
                
    except arxiv.UnexpectedEmptyPageError as e:
        print("Se han recuperado todos los resultados disponibles")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

print(f"Se han exportado las entradas posteriores a 2017 al archivo '{output_file}'. Consulta usada:")
print(formatted_query)
print(f"Número de entradas exportadas: {count}")
print(f"Número de entradas filtradas por año: {filtered_by_year}")
print(f"Número de entradas filtradas por falta de palabras clave de ambos grupos: {filtered_by_keywords}")
