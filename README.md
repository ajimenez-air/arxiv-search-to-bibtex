# Script de búsqueda en arXiv y conversión a BibTeX
Este script permite realizar búsquedas en arXiv y obtener los resultados en formato BibTeX.

## Requisitos

### Clona el repositorio
    ```bash
    git clone https://github.com/ajimenez-air/arxiv-search-to-bibtex.git
    ```
- Python 3.6+
- Paquete `arxiv` instalar con:
    ```bash
    pip install arxiv
    ```


## Uso

1. Modifica el archivo `query.txt` con tu consulta de búsqueda usando el formato de este ejemplo:
    ```
    (
    (Term1 OR Term2 OR Term3)
    AND
    (
        (TermA OR TermB OR TermC)
        OR
        (
        (Term1 OR Term2)
        AND
        (Term3 OR Term4)
        AND
        (Term5 OR Term6)
        )
    )
    OR
    (
        (Term1 OR Term2)
        AND
        (Term3 OR Term4)
        AND
        (Term5 OR Term6)
    )
    )
    ```
2. Ejecuta el script con:
    ```bash
   python arxiv-search.py
   ```

3. El script escribe los resultados de la búsqueda en un archivo llamado `resultados_arxiv.bib` en formato BibTex.
    - La búsqueda ahora mismo está limitada a 100 resultados. Se puede modificar en el campo `max_results=100` del script. Pero si hay muchas la API no devuelve todos los resultados.
