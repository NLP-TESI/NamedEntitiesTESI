# How to execute
	python3 main.py [opções]

## Options
1. preprocess: pre-process the text. This should be executed once before of any other option.
2. find_ne: extract named entities and relationships.
3. tfidf: calculate o tfidf.
4. query: enter in query mode. In query mode you can make term searchs.
5. svd: enable SVD for query mode. Only execute if in query mode.

## Example

	python3 main.py preprocess find_ne tfidf query svd

