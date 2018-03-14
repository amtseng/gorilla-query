import sys
import os
import argparse
import mechanize
import urlparse
from bs4 import BeautifulSoup

GORILLA_URL = "http://cbl-gorilla.cs.technion.ac.il/"
GO_ONTOS = {"process": "GOResultsPROCESS.html", "function": "GOResultsFUNCTION.html", "component": "GOResultsCOMPONENT.html"}

def parse_arguments():
	"""
	Parses arguments and returns a dictionary of the arguments.
	"""
	parser = argparse.ArgumentParser(description="Submits genes to GOrilla for term enrichment analysis")
	parser.add_argument("-o", "--outdir", type=str, required=True, help="Directory to output the enrichment tables")
	parser.add_argument("-g", "--genefile", type=str, help="Path to a file containing newline-delimited genes, preferably as gene symbols")
	parser.add_argument("-i", "--id", type=str, help="ID of an existing GOrilla run, to skip directly to results scrape")
	
	args = parser.parse_args()

	genefile, outdir, run_id = args.genefile, args.outdir, args.id

	if (not genefile and not run_id) or (genefile and run_id):
		print("Error: Need either a gene list or a run ID (exactly one)")

	if genefile:
		with open(genefile, "r") as f:
			gene_list = [line.strip() for line in f]
	else:
		gene_list = None
	
	return {
		"g": gene_list,
		"o": outdir,
		"i": run_id
	}


def submit_gorilla(gene_list):
	"""
	Sends the gene list to GOrilla and returns the base URL for the results.
	"""
	br = mechanize.Browser()
	br.set_handle_redirect(mechanize.HTTPRedirectHandler)
	
	br.open(GORILLA_URL)
	br.select_form(nr=0)
	br.form["target_set"] = "\n".join(gene_list)
	br.form["db"] = ["all"]
	
	br.submit()

	url = str(br.geturl())
	url_tokens = url.split("/")
	return "/".join(url_tokens[:-1])


def scrape_gorilla(base_url, page_name):
	"""
	Scrapes the results page given by the base URL and the specific page name
	(e.g. GOResultsPROCESS.html). The results are scraped down as a list of
	tuples:
		term ID, description, p val, FDR, enrichment, N, B, n, b, genes	
	Returns the URL, total number of genes tested, and this list of tuples.
	"""
	url = "/".join([base_url, page_name])

	br = mechanize.Browser()
	br.set_handle_redirect(mechanize.HTTPRedirectHandler)
	br.open(url)
	soup = BeautifulSoup(br.response().read(), "lxml")

	if str(soup.title.text) == "No GO Enrichment Found":
		return url, 0, []

	results_table = soup.find_all("table")[1]  # Second table on the page
	
	table_entries = []  # GO term, description, p, FDR, enrichment, B, n, b, genes
	N = ""
	for row in results_table.find_all("tr")[1:]:  # First row is header
		row_data = [entry.text for entry in row.find_all("td")]
		term, desc, pval, fdr = [str(entry) for entry in row_data[:4]]
		
		enrich_data = str(row_data[4]).split()
		enrich = enrich_data[0]
		counts = enrich_data[1][1:-1].split(",")
		N = counts[0]
			
		gene_pairs = str(row_data[5]).strip().split("\r\n")[1:]  # First entry is '[+] Show genes'
		gene_pairs = [pair.split("-") for pair in gene_pairs]
		genes = {pair[0].strip() : pair[1].strip() for pair in gene_pairs}
		table_entries.append((term, desc, pval, fdr, enrich, counts[1], counts[2], counts[3], genes))

	return url, N, table_entries


def write_table(url, total_genes, table_entries, outpath):
	"""
	Writes the table entries returned by `scrape_gorilla` to the path given.
	"""
	with open(outpath, "w") as outfile:
		header = "\t".join(["term", "desc", "pval", "fdr", "enrichment", "B", "n", "b", "genes"])
		outfile.write("# URL: {0}\n".format(url))
		outfile.write("# Total genes: {0}\n".format(total_genes))
		outfile.write(header + "\n")

		for row in table_entries:
			row_data = list(row[:-1])
			row_data += [",".join(row[-1].keys())]  # Only write gene names
			outfile.write("\t".join(row_data) + "\n")


if __name__ == "__main__":
	arg_dict = parse_arguments()
	gene_list = arg_dict["g"]
	outdir = arg_dict["o"]
	run_id = arg_dict["i"]

	if not os.path.isdir(outdir):
		os.mkdir(outdir)

	if gene_list:
		print("Submitting to GOrilla...")
		base_url = submit_gorilla(gene_list)
	elif run_id:
		base_url = "/".join([GORILLA_URL, "GOrilla", run_id])

	for onto_type in GO_ONTOS:
		print("Scraping results for GO {0}...".format(onto_type.upper()))
		url, N, table = scrape_gorilla(base_url, GO_ONTOS[onto_type])
		outpath = os.path.join(outdir, "{0}.tsv".format(onto_type))
		write_table(url, N, table, outpath)
