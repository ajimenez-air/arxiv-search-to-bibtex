# Script de búsqueda en arXiv y conversión a BibTeX
Este script permite realizar búsquedas en arXiv y obtener los resultados en formato BibTeX.

## Requisitos

- Python 3.6+
- Paquete `arxiv` instalar con:
    ```bash
    pip install arxiv
    ```

## Uso

1. Modifica el archivo `query.txt` con tu consulta de búsqueda usando el siguiente formato:
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
