# dataset_aws-price-list

This repo holds everything your team needs to start on the AWS Price List Bulk API offer files, the
machine-readable price sheet that Amazon Web Services publishes for everything it sells. One row is one
price: one product, under one purchase term, at one rate, in one region, on the day the file was published.
The EC2 compute price sheet for Northern Virginia alone is 394,515 rows by 93 columns, and Amazon's EC2
version index lists 122 past versions of that sheet, the oldest in force from 1 December 2015. This repo
holds the data overview document, a small sample of every table so you can start reading code before
anything finishes downloading, and a script that downloads the real files.

**A note on accuracy.** The documents here were written with AI assistance and then checked against the linked official sources. Linked sources are authoritative. Unlinked statements, and anything marked "(unverified)", should be checked before you rely on them. Report mistakes to the professor.

## Files

- `data_overview_aws-price-list.md`: the dataset description, covering industry context, possible
  stakeholders and decisions (illustrative examples only), what is already known, download instructions,
  the full data dictionary and the traps.
- `download_data.py`: downloads the eleven data files into a `data` folder next to the script.
- `sample/`: eleven small files, one per table, plus a README saying how they were drawn.
- `.gitignore`: keeps the downloaded `data` folder out of Git.

## Get the files

```
cd ~/dso576
git clone https://github.com/USC-DSO-576-PS/dataset_aws-price-list.git
cd dataset_aws-price-list
uv run python download_data.py
```

If `git clone` asks for a username and password, you have not been added to the repo yet: use Route A and tell the professor. Route A is the browser download, described in section 4 of the data overview document. Use Route A as well if `download_data.py` fails or prints an HTTP error: some networks block scripted requests, and the browser route produces the same eleven files with the same names.

That downloads 643 MB. Section 4 of the data overview document explains what it downloads, how long it takes,
how much disk space you need, why one address on this endpoint is a 6 GB file you must not click, and how to
open the files in pandas, including the two arguments they will not open correctly without.

This repo is read-only for students: read it, clone it, but do not push to it. Copy
`data_overview_aws-price-list.md` into your team's `project` folder as the Module 3 handout asks.
