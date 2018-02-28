### GOrilla Query
#### Background
Despite the awful acronym (if it can even be called one), [GOrilla](http://cbl-gorilla.cs.technion.ac.il/) is an excellent tool to discover GO term enrichments in a ranking of genes. Unfortunately, the tool is only available (to my knowledge) through a web interface, so I wrote this small script to query GOrilla programmatically, from commandline. This script allows the user to submit an enrichment query for a single target ranking of genes, for _H. sapiens_, and then scrapes down the results for GO Biological Process, Function, and Component.
Other functionalities to take advantage of other GOrilla usages can be easily extended from this script.

#### Usage
`python gorilla_query.py -g [GENE_LIST] -o [OUTPUT_DIR]`
- `GENE_LIST`
	- A file containing a ranking of `\n`-delimited genes
	- Genes are preferably given as official gene symbols, but Ensembl IDs are also acceptable (see [the web interface](http://cbl-gorilla.cs.technion.ac.il/) for more details
- `OUTPUT_DIR`
	- GOrilla Query outputs three files into this directory (which is created if it does not exist already), corresponding to the gene enrichment tables for Process, Function, and Component
	- Files will be `OUTPUT_DIR/process.tsv`, `OUTPUT_DIR/function.tsv`, and `OUTPUT_DIR/component.tsv`

#### Output
Each output table consists of the following:

**Line 1:** A stable web link (for about 1 month) to the results on GOrilla's servers (this link also contains more information about results)

**Line 2:** The total number of genes tested by GOrilla, **N**

**Line 3:** Header of the results table

**Lines 4-n:** Rows of the results table, in decreasing order of significance
The following is a description of each column:
- `term`: The GO-term ID (e.g. `GO0051302`)
- `desc`: The description of the GO-term (e.g. `regulation of cell division`)
- `pval`: p-value of the term enrichment, uncorrected for multiple hypothesis testing
- `fdr`: FDR of the term enrichment, corrected for multiple hypothesis testing
- `enrichment`: Enrichment value, calculated as **(b/n) / (B/N)**
- `B`: The total number of genes associated with this term, **B**
- `n`: The number of genes that appear at the top of the ranking (see the citation below for more details), **n**
- `b`: The intersection of genes that appear at the top of the ranking and the genes associated with the term, **b**

#### Citations
Eran Eden*, Roy Navon*, Israel Steinfeld, Doron Lipson and Zohar Yakhini. "**GOrilla: A Tool For Discovery And Visualization of Enriched GO Terms in Ranked Gene Lists**", [BMC Bioinformatics 2009, 10:48](http://www.biomedcentral.com/1471-2105/10/48).

