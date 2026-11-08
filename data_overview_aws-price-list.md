# AWS Price List Bulk API offer files

Published by [Amazon Web Services](https://aws.amazon.com/). The public list price of the products AWS sells, as machine-readable files: a current price sheet for each of the 269 services listed in [the service index](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json), for EC2 in up to the 106 regions listed in its region index, plus past versions of each sheet, reaching back to December 2015 for EC2.

**How to use this document.** Copy it into your team's `project` folder, as the Module 3 handout asks, and keep it open while you work. Everyone on the team should read sections 1 to 3 before the workshop. Section 4 is the download procedure, so Role 5 (Technical path) follows it step by step and records what happened. Sections 5 and 6 are the column-level detail and the traps, so Role 3 (Data fit) leans on them to answer what one row is, what was observed and when, which columns carry evidence, and what was never recorded at all.

**How much to trust this document.** It was written with AI assistance and then checked, claim by claim, against the sources linked throughout. Where a sentence links to a source, that source is the authority: if the two disagree, the source wins. Where a sentence has no link, it was either read directly from the data files or is a general statement that could not be tied to one source. Treat those as useful but unconfirmed, and check them before you rely on them in a deliverable. Anything that could not be confirmed at all was either removed or is marked "(unverified)". If you find a mistake, tell the professor so it can be fixed for every team.

---

## 1. Description and industry context

Amazon Web Services (AWS) rents computers by the hour. A company that needs a server does not buy one and put it in a room; it rents one from AWS, uses it for an hour or a year, and stops paying when it stops using it. That business is called **cloud computing**, and AWS is one of several companies that sell it at global scale. The rented computer is called an **instance**. The service that sells instances is called **EC2**, short for [Elastic Compute Cloud](https://aws.amazon.com/ec2/). AWS also sells managed databases ([**RDS**, Relational Database Service](https://aws.amazon.com/rds/)), file storage ([**S3**, Simple Storage Service](https://aws.amazon.com/s3/)), a service that runs a piece of code on demand without any server to manage ([**Lambda**](https://aws.amazon.com/lambda/)), a machine-learning platform ([**SageMaker**](https://aws.amazon.com/sagemaker-ai/)), and access to large language models by the token ([**Bedrock**](https://aws.amazon.com/bedrock/)). A **token** is roughly a word fragment: language models are billed by how many tokens go in and how many come out.

AWS publishes the list price of all of this, openly, in files. There is one file per service, and for the big services one file per **region** as well. A region is a geographic cluster of AWS data centers ([AWS Global Infrastructure](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/)), named like `us-east-1` (Northern Virginia) or `eu-west-1` (Ireland). The same instance costs different amounts in different regions. AWS calls each of these files an **offer**, and the whole collection is the [**Price List Bulk API**](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api.html). Amazon's own instructions for [getting price list files manually](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html) are to navigate to a URL: there is no account to make, no key to get and no form to fill in. Every file is a plain public download over HTTPS.

**One row is one price.** More precisely: one product, under one purchase term, at one rate, in one region, on the day the file was published. Read aloud, a row says something like "renting one m5.xlarge instance running Linux on shared hardware in US East (Northern Virginia), paid by the hour with no commitment, costs $0.1920 per hour." The EC2 price sheet for Northern Virginia alone is 394,515 such rows across 93 columns, because 1,563 instance types appear in that one file, each priced under up to six operating systems, four values of hardware tenancy, and up to twenty reserved-term combinations on top of the on-demand rate, and every combination is its own row.

**AWS republishes an offer when prices inside it change,** and past versions stay at their own addresses. For EC2 the version index lists 122 published versions, the oldest in force from 1 December 2015 and the newest from 1 September 2026, one a month since January 2017. So the same web address gives you both today's price sheet and a monthly price history going back a decade. Most companies do not publish a machine-readable archive of the prices they have charged.

Now the industry. Cloud spending is a large controllable line item for a technology company, and a profession called [**FinOps**](https://www.finops.org/) (financial operations for cloud) exists to manage it. A FinOps analyst's job is to decide which region to run a workload in, whether to commit to a one-year or three-year term in exchange for a discount, which chip generation to move to, and whether a managed service is worth its premium over a raw instance. Those decisions are worth a great deal of money: the largest single number in the 4 September 2026 EC2 us-east-1 file is $13,370,513, a three-year all-upfront fee for a `u7in-32tb.224xlarge`. The people who care about these numbers are cloud customers deciding what to buy, the software vendors who build cost-management tools on top of the data, procurement teams who need a benchmark before they negotiate, and journalists and analysts who want to describe what is happening to the price of computing.

Four things separate someone who reads these files as an insider from someone who does not. First, **these are list prices.** Large customers negotiate private pricing agreements and receive credits, and none of that is public or in these files, so a real bill can sit well below these numbers. Any product built on this data has to say so on its first slide. Second, **the operating system bundled into the hourly rate is a large source of price spread at fixed hardware.** The same physical machine costs one price with Linux and a higher one with Windows, because the Windows license is folded into the hourly rate: an m5.xlarge in us-east-1 is listed at $0.1920 per hour on Linux, $0.3760 with a Windows license included, and $1.8760 with Windows and SQL Server Enterprise. Rows carrying a bundled Microsoft SQL Server edition are 183,904 of the 394,515 EC2 rows, just under half. Third, **Amazon designs its own processors**, [a family called Graviton](https://aws.amazon.com/ec2/graviton/), and sells them alongside Intel and AMD chips; the `Physical Processor` column is what lets you see what Amazon charges for its own silicon. Fourth, **there are several ways to buy the same instance** and they are not comparable without work: [on demand](https://aws.amazon.com/ec2/pricing/) (pay by the hour, cancel any time), [reserved](https://aws.amazon.com/ec2/pricing/reserved-instances/) (commit to one or three years for a discount, paying some or all of it up front), and, outside these files, [spot](https://aws.amazon.com/ec2/spot/) (spare capacity at a variable price) and [Savings Plans](https://aws.amazon.com/savingsplans/). A three-year all-upfront reservation on an m5.xlarge is listed 62 percent below its on-demand rate, which is why the commitment question is worth a whole job.

---

## 2. Possible stakeholders and decisions (illustrative examples only)

The bullets below are illustrative examples only. They were generated with AI help to show the shape an audience statement can take with this data. They are not the professor's suggestions, not a list to choose from, and not necessarily good choices: a named organization may not make this decision the way the bullet implies, and a decision that reads well here may not survive contact with the data. Treat each one as a hypothesis to test, in the sense the Module 3 handout uses, and expect your team to find, check and defend its own audience.

- **A FinOps analyst at [Netflix](https://about.netflix.com/en/news/completing-the-netflix-cloud-migration) must decide which AWS region to place a new nightly video encoding batch job in.** `Instance Type`, `vCPU`, `Memory`, `PricePerUnit` and `Region Code`, held at one operating system and tenancy, give the list cost of the same hardware in each region.
- **A cloud cost consultant at [The Duckbill Group](https://www.duckbillgroup.com/) must decide whether to recommend a three-year all-upfront reservation to a client's engineering team.** The `TermType`, `LeaseContractLength`, `PurchaseOption` and `OfferingClass` columns, with the paired upfront-fee and hourly rows, give the full discount curve for any instance type.
- **A procurement lead at [USC Information Technology Services](https://itservices.usc.edu/) must decide what benchmark number to bring into a contract conversation with AWS.** The published list price for each product the university already uses is the public starting point that a negotiated rate is measured against.
- **An AI product manager at [Harvey](https://www.harvey.ai/), the legal AI company, must decide which language model to serve their contract summarizer from, and in which region.** The two Bedrock files give input, output, cached and batch token prices for 139 named models across 35 and 36 regions.
- **A pricing manager at [Anthropic](https://www.anthropic.com/) must decide where their next model should sit against rival models on [Bedrock](https://aws.amazon.com/bedrock/).** `serviceName`, `Model`, `Provider`, `Inference Type` and `PricePerUnit` across the two Bedrock files give the published per-token price of the models AWS sells, by vendor and by region.
- **A technology reporter at the [Los Angeles Times](https://www.latimes.com/) must decide whether a claim about the direction of cloud prices is publishable.** The archived versions of the EC2 offer are the published record of what AWS listed on any given date, and any reader can check them at the same addresses.
- **A database architect at a hospital software vendor must decide between Oracle and PostgreSQL for a new records product.** RDS `Database Engine`, `Database Edition`, `License Model` and `Deployment Option` price the same hardware under each engine and each way of copying the database across data centers for reliability.
- **An engineering manager at the [Broad Institute](https://www.broadinstitute.org/) must decide whether to keep training genomics models on SageMaker or move them to plain EC2 instances.** Most SageMaker `Instance Name` values are an EC2 instance type behind an `ml.` prefix, so for those the premium charged for the managed service on the same hardware can be read off; see section 5.4 for the values where that does not hold.

---

## 3. What is already well known and demonstrated

> Your project is judged on how far it goes beyond what is listed here. Reproducing these is a fine way to
> learn the data, but it earns little credit on its own, and a build that hiring managers have seen many
> times is a weak portfolio piece. Read this list as the floor, not as a menu.

### (a) Findings people already know

- Instances built on Amazon's own Graviton processors are usually listed below Intel and AMD instances of the same vCPU count and memory. AWS's own [Graviton page](https://aws.amazon.com/ec2/graviton/) claims Graviton-based instances "cost up to 20% less than comparable x86-based Amazon EC2 instances"; in the 4 September 2026 us-east-1 download, of the 63 (vCPU, memory) shapes offered on both, the cheapest Graviton row is below the cheapest Intel or AMD row in 54.
- The same instance costs different amounts in different regions. In the 4 September 2026 download, of the 1,087 on-demand Linux instance types priced in both `us-east-1` and `eu-west-1`, Ireland is dearer on 1,086 of them, by about 12 percent at the median.
- Committing to a reserved term buys a discount, and the discount grows with the length of the term and with how much you pay up front. The worked table in section 5.10 shows the shape of it.
- Windows and bundled Microsoft SQL Server carry a large license premium over Linux on identical hardware. In the 4 September 2026 us-east-1 download, an m5.xlarge is $0.1920 per hour on Linux, $0.3760 with a Windows license included, and $1.8760 with Windows and SQL Server Enterprise.
- [Savings Plans](https://aws.amazon.com/savingsplans/), a commitment product that is not in these files, is AWS's current flexible-commitment offering alongside reserved instances.
- Very few large customers pay list price; negotiated private pricing agreements, credits and startup programs all sit below it, and none of them is public.
- [Spot capacity](https://aws.amazon.com/ec2/spot/), which is sold from a separate feed and is not in these files, is advertised by AWS at "up to a 90% discount compared to On-Demand prices" and its price varies over time.

### (b) Analyses and tools that already exist

- [vantage-sh/ec2instances.info](https://github.com/vantage-sh/ec2instances.info) and the site it powers, [instances.vantage.sh](https://instances.vantage.sh): an MIT-licensed, actively maintained instance comparison table with filters, covering AWS EC2, RDS, ElastiCache, Redshift and OpenSearch, plus virtual machines on Azure and Google Cloud. **It is finished and its code is public.**
- [CloudPrice](https://cloudprice.net) and [Holori](https://holori.com): two commercial cross-cloud price comparison sites, both covering AWS, Azure and Google Cloud.
- [AWS Pricing Calculator](https://calculator.aws): Amazon's own official tool, which turns these same prices into a per-customer cost estimate.
- [aws-samples/service-price-lists-collector](https://github.com/aws-samples/service-price-lists-collector): an AWS sample repository, in Python, that fetches the bulk offer files and exports them to CSV, JSON and Excel. Last updated August 2025.
- [aliscott/aws-prices-graphql](https://github.com/aliscott/aws-prices-graphql): a GraphQL query interface built over the bulk price list, in JavaScript. Last updated March 2022.
- [lyft/awspricing](https://github.com/lyft/awspricing), also on [PyPI](https://pypi.org/project/awspricing): a Python library from Lyft that reads offer files, including past versions. Last released in 2019.
- [erans/ec2instancespricing](https://github.com/erans/ec2instancespricing), [y13i/awsprice](https://github.com/y13i/awsprice), [ajelenak/aws-price-list](https://github.com/ajelenak/aws-price-list) and [wnameless/aws-price-list-api](https://github.com/wnameless/aws-price-list-api): four more open wrappers that download and parse the same files, in Python, Go and Java, all last updated between 2017 and 2023. **Several open loaders for these files already exist.**
- [awslabs AWS Pricing MCP Server](https://awslabs.github.io/mcp/servers/aws-pricing-mcp-server): an official Apache-2.0 server in the [awslabs/mcp](https://github.com/awslabs/mcp) repository that hands AWS prices to an AI assistant on request.
- [kenklin/aws-price-comparison-chart](https://github.com/kenklin/aws-price-comparison-chart): an interactive EC2 price comparison chart in JavaScript, last updated December 2014, so it predates the current offer-file format.
- [AWS Pricing Dataset](https://www.kaggle.com/datasets/justsahil/aws-pricing-dataset) on Kaggle, described by its author as a weekly pull covering all AWS services. Two more near-identical Kaggle copies of the same price list exist, one from 2019 and one from 2021; the link above is the current one, and the others add nothing.
- [AgentOps-AI/tokencost](https://github.com/AgentOps-AI/tokencost): an MIT-licensed Python package of token prices, synced from the LiteLLM cost tracker; its shipped price file holds entries for over a thousand models.
- [simonw/llm-prices](https://github.com/simonw/llm-prices) and its site [llm-prices.com](https://www.llm-prices.com): a curated cross-provider table of language model prices, including Amazon's Nova models.
- [fstandhartinger/model-market-comparison](https://github.com/fstandhartinger/model-market-comparison): a comparison of language model prices across providers including AWS Bedrock, normalized to a price per million tokens.
- [pricepertoken.com](https://pricepertoken.com), a commercial site comparing token prices across more than 300 models, and the [LLM Pricing Tracker](https://joshuaqsh.github.io/posts/llm-pricing-tracker/), a personal blog post with an interactive tracker covering providers other than AWS.
- [ericpauley/aws-spot-price-history](https://github.com/ericpauley/aws-spot-price-history): a collector for a monthly archive of EC2 **spot** price history across regions, with the archive itself now hosted on Zenodo. Note that spot prices come from a different AWS feed and are not in these files, so this is a different dataset with a similar name.
- [Predicting EC2 Spot Prices](https://www.kaggle.com/code/princeashburton/predicting-ec2-spot-prices), a 2018 Kaggle notebook, and the [AWS Spot Pricing Market](https://www.kaggle.com/datasets/noqcks/aws-spot-pricing-market) dataset it runs on, last modified in 2017. A third Kaggle set named `aws_pricing` is a near-identical copy of the same spot history under a misleading name. **All of it is spot data, which is not in this dataset.**

---

## 4. How to obtain the data

**Where it comes from.** Amazon documents the download addresses at [Getting price list files manually](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html), part of the [AWS Price List Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api.html) documentation. The list of every service that has a price list is at [the service index](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json). That page tells you to navigate to a URL, and no account, key, login or form is involved.

**Terms.** These files carry no open-data license. Instead every one of them carries this line as its second row, quoted here exactly as it appears in the 4 September 2026 EC2 file: "This pricing list is for informational purposes only. All prices are subject to the additional terms included in the pricing pages on `http://aws.amazon.com`. All Free Tier prices are also subject to the terms included at `https://aws.amazon.com/free/`". Reproduce that disclaimer in anything you publish from this data, and never present a number from these files as what a customer will actually be billed.

**Update cadence.** AWS publishes a new version of an offer when prices in it change, and each published version keeps its own address. In the EC2 version index the versions come one a month from January 2017 onward. This has one consequence you must plan for: the word `current` in a download address does not mean a fixed file. Re-run the download next week and you may get a different version. Line 4 of every file you download is the version stamp, so record it whenever you report a number.

### The address pattern, and the 6 GB warning

Every price list lives at an address built the same way:

```
https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/{service}/{version}/{region}/index.csv
```

`{service}` is a code such as `AmazonEC2` or `AWSLambda`. `{version}` is either the word `current` or a 14-digit stamp such as `20250828212014`. `{region}` is a region code such as `us-east-1`. This is the pattern Amazon documents at [Getting price list files manually](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html), where `current` is described as pointing to the latest published version.

> **Warning: leave out the region and you get a very large file.** The address
> `.../AmazonEC2/current/index.csv`, with no region in it, is the **all-region** EC2 price list, and the
> server reported it as **5,957,234,980 bytes, about 6 GB**, on 5 September 2026. It holds every region at
> once. It will take a long time to arrive, it will fill a laptop disk, and it will not open in pandas on a
> normal machine. **Do not download it.** The address you want has the region code in it:
> `.../AmazonEC2/current/us-east-1/index.csv`, which the server reported as 303 MB on the same day.
> The all-region RDS file has the same problem at a smaller scale, 341 MB against 18 MB for one region.
>
> This trap catches people because both addresses look almost identical and both return a normal HTTP 200
> response. The only difference is the region code. Read the address twice before you press Enter.
>
> The rule of thumb: for **EC2 and RDS**, always name a region. For **SageMaker, S3, Lambda and the two
> Bedrock offers**, the all-region file is only 2 to 23 MB, so leaving the region out is the convenient
> choice and is what the table below does.

### The files to download

Eleven files, 643 MB in total. Eight are price lists and three are small index files that tell you what else exists. Every size below is the `Content-Length` Amazon's server reported for that address on 5 September 2026; row and column counts were read from the files themselves.

| File name to save as | Direct link | Format | Size (MB) | Rows | Columns |
|---|---|---|---|---|---|
| `ec2_us-east-1.csv` | [EC2, US East (N. Virginia)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/us-east-1/index.csv) | CSV | 303.5 | 394,515 | 93 |
| `ec2_eu-west-1.csv` | [EC2, EU (Ireland)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/eu-west-1/index.csv) | CSV | 282.1 | 369,916 | 93 |
| `rds_us-east-1.csv` | [RDS, US East (N. Virginia)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.csv) | CSV | 18.1 | 30,485 | 58 |
| `sagemaker_all.csv` | [SageMaker, all regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonSageMaker/current/index.csv) | CSV | 23.2 | 40,654 | 67 |
| `s3_all.csv` | [S3, all regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/index.csv) | CSV | 4.3 | 9,943 | 35 |
| `lambda_all.csv` | [Lambda, all regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSLambda/current/index.csv) | CSV | 4.4 | 10,620 | 24 |
| `bedrock_foundation_models.csv` | [Bedrock Marketplace models, all regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/current/index.csv) | CSV | 2.1 | 5,669 | 17 |
| `bedrock_service_all.csv` | [Bedrock service, all regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/index.csv) | CSV | 5.3 | 11,657 | 35 |
| `offer_index.json` | [Service index, all 269 offers](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json) | JSON | 0.09 | 269 offers | up to 6 fields |
| `ec2_version_index.json` | [EC2 version index, all 122 versions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/index.json) | JSON | 0.03 | 122 versions | 3 fields |
| `ec2_region_index.json` | [EC2 region index, all 106 regions](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json) | JSON | 0.02 | 106 regions | 2 fields |

Row and column counts exclude the five metadata lines and the header line. Leave at least 2 GB free on the disk: 643 MB for the files themselves, and room for pandas to work while it reads the largest one.

Nothing here is a zip file, a tar file or any other archive. Every download is a plain CSV or a plain JSON file, so there is nothing to unpack on either Mac or Windows.

### Route A: download in a browser

1. Clone this repository with the first three lines of the Route B block below, so that you have a folder named `dataset_aws-price-list` on your computer.
2. Make the folder the files will go into. In the same Terminal or PowerShell window, still inside `dataset_aws-price-list`, run this one line:

   ```
   mkdir data
   ```

3. Open the table above in your browser and click the eleven links, one at a time. Chrome, Edge and Safari all start the download at once for the CSV links. The three JSON links may open as text in the browser window instead of downloading: if that happens, go back, right-click the link and choose **Save link as**.
4. Rename each downloaded file to the name in the first column of the table. This matters: every one of them arrives from the server called `index.csv` or `index.json`, so downloading two of them in a row gives you `index.csv` and `index (1).csv`, and you will not know which is which. Rename each one as soon as it lands.
5. Move the eleven renamed files from your Downloads folder into the `data` folder you made, then check that the file sizes roughly match the table.

The two EC2 files are the slow part, at 303 MB and 282 MB; how long the whole set takes depends on your connection. Nothing on this endpoint asks for a login, a click sequence, a CAPTCHA or an email address, and no browser extension is needed. If a download stalls part way, start that one file again.

Because of the renaming step, Route B is easier. Use Route A if a corporate network or a firewall blocks the script, or if the script fails for any other reason: the two routes produce the same eleven files with the same names in the same folder.

### Route B: download with the script in this repository

Open Terminal on Mac or PowerShell on Windows and run these four lines, one at a time:

```
cd ~/dso576
git clone https://github.com/USC-DSO-576-PS/dataset_aws-price-list.git
cd dataset_aws-price-list
uv run python download_data.py
```

If `git clone` asks for a username and password, you have not been added to the repo yet: use Route A and tell the professor.

The script makes a folder named `data` next to itself and downloads all eleven files into it, already correctly named. It prints one line per file with the file name, the size in MB and the seconds it took, then either `checksum ok` or `checksum differs (the publisher may have updated the file)`, and it ends with a one-line summary. How long the run takes depends on your connection.

**A `checksum differs` line is normal here and is not an error.** The fingerprints built into the script were recorded on 5 September 2026. Because these addresses always serve the newest published version, AWS will have republished some of these offers since then, and a republished file has a different fingerprint. The line is telling you that you are holding a newer price sheet than the one this document describes, which is useful to know and worth writing down. Check line 4 of the file for the version stamp you actually have.

Two extra options:

```
uv run python download_data.py --check
```

downloads nothing at all. It asks Amazon's server for the size of every file and reports whether each still matches the table above. Run it first if you want to see what you are about to pull down.

```
uv run python download_data.py --small
```

skips the two large EC2 files and fetches only the nine small ones, about 57 MB. Useful on a slow connection or when you only need the RDS, SageMaker, S3, Lambda and Bedrock price sheets.

If your connection drops part way through a full run, run the command again: files that are already complete are skipped, so only the unfinished ones are fetched again.

**If the script fails, use the browser instead.** Some networks and some servers block scripted requests, and a script that works on one machine can fail on another. If `download_data.py` prints an HTTP error, a connection error, `FAILED`, or `no answer`, do not spend time debugging it. Go to Route A above, click the eleven links in the table, rename each file to the name in the first column, and put the eleven files in the `data` folder next to `download_data.py`. That is the same folder the script would have written to, with the same eleven names, so every snippet in this document then works unchanged. Route A covers every file the script downloads.

### The five metadata lines above the header

**This is the single most important thing to know before you open one of these CSV files.** Amazon documents this in [Reading the service price list file](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-service-price-list-file-for-services.html): "The first five rows of the CSV file contain the metadata for the price list file. The sixth row has the column names." They are not column names and they are not data. Each is a two-field row: a label and a value. Here are the five lines at the top of `lambda_all.csv`, with the disclaimer text shortened:

```
"FormatVersion","v1.0"
"Disclaimer","This pricing list is for informational purposes only. ..."
"Publication Date","2026-08-31T09:23:18Z"
"Version","20260831092318"
"OfferCode","AWSLambda"
```

Line 6 is the real header row with the column names. Data starts on line 7.

If you call `pd.read_csv()` without telling it to skip those five lines, pandas takes line 1 as the header, decides the file has two columns, and hands you a table of nonsense. The fix is one argument: **`skiprows=5`**. That number is not a guess about how many rows to throw away; it is exactly the five metadata lines, and line 6 then becomes the header, which is what you want.

Every snippet below is complete on its own. Save one as a file such as `look.py` inside your `dataset_aws-price-list` folder, then run it with `uv run python look.py`.

Those five lines are worth reading, not just skipping. `Publication Date` and `Version` tell you which build of the price sheet you are holding. `Version` is also the string you put back into a download address to fetch that exact file again later. Read them like this:

```python
import pandas as pd

meta = pd.read_csv("data/ec2_us-east-1.csv", nrows=5, header=None,
                   names=["field", "value"])
print(meta)
```

That prints the five rows above: `FormatVersion` `v1.0`, then the disclaimer, then `Publication Date` `2026-09-04T23:11:17Z`, then `Version` `20260904231117`, then `OfferCode` `AmazonEC2`. Write the `Version` value into your notes next to any number you report.

### Opening the files in pandas

The EC2 price list for one region, 394,515 rows by 93 columns. Read everything as text: `PricePerUnit` is a fixed-decimal string such as `0.1920000000`, `EndingRange` holds the literal word `Inf`, and `Memory` reads `16 GiB` with the unit attached.

```python
import pandas as pd

ec2 = pd.read_csv("data/ec2_us-east-1.csv", skiprows=5, dtype=str,
                  keep_default_na=False, low_memory=False)
print(ec2.shape)
print(ec2["TermType"].value_counts())
```

That prints `(394515, 93)`, then `Reserved` at 273,971 rows and `OnDemand` at 120,544.

**Why `keep_default_na=False` is there.** Many columns in these files use the literal two-letter string `NA` to mean "does not apply", for example `Pre Installed S/W` on an instance with no bundled software. By default pandas treats the text `NA` as a missing value and turns it into `NaN`, even with `dtype=str`. That silently destroys real values: without this argument, filtering on `Pre Installed S/W == "NA"` matches zero rows. With it, the same filter matches 210,518 rows, which is the correct answer. `low_memory=False` stops pandas from guessing a column's type from the first chunk of a large file and then warning about it. Reading this file takes several seconds and well over a gigabyte of memory, so close other notebooks first.

Six columns have to be held fixed before any two EC2 rows are comparable, because the same physical machine appears many times under different operating systems, tenancies and capacity states:

```python
import pandas as pd

ec2 = pd.read_csv("data/ec2_us-east-1.csv", skiprows=5, dtype=str,
                  keep_default_na=False, low_memory=False)
compute = ec2[(ec2["Product Family"] == "Compute Instance") &
              (ec2["TermType"] == "OnDemand") &
              (ec2["Operating System"] == "Linux") &
              (ec2["Tenancy"] == "Shared") &
              (ec2["CapacityStatus"] == "Used") &
              (ec2["Pre Installed S/W"] == "NA")]
print(compute.shape)
print(compute["Instance Type"].nunique())
```

That prints `(1251, 93)` and then `1245`. Out of 394,515 rows, 1,251 are the plain on-demand Linux compute rows, covering 1,245 distinct instance types. Drop any one of the six filters and the row count multiplies and every average you compute changes.

The two Bedrock files, which hold the language model token prices, open the same way:

```python
import pandas as pd

fm = pd.read_csv("data/bedrock_foundation_models.csv", skiprows=5, dtype=str,
                 keep_default_na=False, low_memory=False)
print(fm.shape)
print(fm["serviceName"].value_counts().head(3))

bedrock = pd.read_csv("data/bedrock_service_all.csv", skiprows=5, dtype=str,
                      keep_default_na=False, low_memory=False)
print(bedrock.shape)
print(bedrock["Inference Type"].value_counts().head(3))
```

That prints `(5669, 17)`, then the three most common model names in that file led by `Claude Sonnet 4.6 (Amazon Bedrock Edition)` at 620 rows, then `(11657, 35)`, then the three most common values of `Inference Type`: `Input tokens` at 1,549 rows, then an empty string at 1,528 rows (the platform-feature rows that are not priced per token), then `Output tokens` at 1,477. The same three arguments open `rds_us-east-1.csv` at `(30485, 58)`, `sagemaker_all.csv` at `(40654, 67)`, `s3_all.csv` at `(9943, 35)` and `lambda_all.csv` at `(10620, 24)`.

### Fetching an older version from the version index

The three index files are small and they are what turns eleven files into a much larger catalog. `ec2_version_index.json` lists all 122 published versions of the EC2 offer with the dates each one was in force. Reading it in pandas:

```python
import json
import pandas as pd

with open("data/ec2_version_index.json") as handle:
    index = json.load(handle)
versions = pd.DataFrame(index["versions"]).transpose()
print(versions.shape)
print(versions.tail(3))
```

That prints `(122, 3)` and then the last three rows of the index. The index is not sorted by date, so sort it yourself before reading it as a series. The row label is the 14-digit version stamp, and the three columns are `versionEffectiveBeginDate`, `versionEffectiveEndDate` and `offerVersionUrl`. The newest version has an empty end date, because it is still in force.

To download one of those older price sheets, put its stamp into the address in place of the word `current`. Save the following as `get_archive.py` inside your `dataset_aws-price-list` folder, change the two values at the top, and run it with `uv run python get_archive.py`:

```python
import json
import urllib.request

VERSION = "20180910235641"
REGION = "us-east-1"

with open("data/ec2_version_index.json") as handle:
    index = json.load(handle)
entry = index["versions"][VERSION]
print("in force from " + entry["versionEffectiveBeginDate"] +
      " to " + entry["versionEffectiveEndDate"])

url = ("https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/" +
       VERSION + "/" + REGION + "/index.csv")
target = "data/ec2_" + REGION + "_" + VERSION + ".csv"
urllib.request.urlretrieve(url, target)
print("saved " + target)
```

Run as written it prints `in force from 2018-08-01T00:00:00Z to 2018-09-01T00:00:00Z` and saves a 33 MB file, the EC2 price sheet for Northern Virginia as it stood in August 2018. It opens with the same `skiprows=5` as every other price list, but it has 77 columns rather than 93, so read the column-drift table in section 5 before stacking it onto a newer file. An archived address names one version stamp rather than `current`, so what it returns does not move under you the way a `current` address does. The same substitution works for a different service (change `AmazonEC2`) or a different region (change `REGION`), and `offer_index.json` and `ec2_region_index.json` list every valid value for those two.

**Start before the download finishes.** The `sample/` folder in this repository already holds eleven small files, including a slice of every table described here, so the team can write and test code straight away while the full files are still arriving.

**Do not commit the downloaded data to your team repository.** The Module 3 handout says so, the files are far too large for GitHub, and anyone can fetch them again from Amazon in minutes. In this repository the `data` folder is already ignored by git.

---

## 5. Data dictionary

Column descriptions below follow the publisher's documentation at [Reading the service price list file for an AWS service](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-service-price-list-file-for-services.html). That page defines only the shared pricing fields, and the definitions taken from it are given in quotation marks. AWS publishes no dictionary for the per-service product attributes, so every entry below that is not in quotation marks, along with every count, percentage and example value, is inferred from the data: it was read from the 31 August to 4 September 2026 download described in section 4. Re-check any of it against your own download before you rely on it.

### Summary

| File | Rows | Columns | Size | What one row is |
|---|---|---|---|---|
| `ec2_us-east-1.csv` | 394,515 | 93 | 303.5 MB | One EC2 compute price in US East (N. Virginia): one instance type, operating system, tenancy and purchase term |
| `ec2_eu-west-1.csv` | 369,916 | 93 | 282.1 MB | The same for EU (Ireland). Identical column layout |
| `rds_us-east-1.csv` | 30,485 | 58 | 18.1 MB | One managed-database price in US East (N. Virginia): 415 database instance types across 13 engines, plus storage and IOPS rates |
| `sagemaker_all.csv` | 40,654 | 67 | 23.2 MB | One SageMaker machine-learning price in one of 39 regions: notebooks, training, hosting, batch transform, clusters |
| `s3_all.csv` | 9,943 | 35 | 4.3 MB | One S3 storage, request or data-transfer price in one of 39 regions |
| `lambda_all.csv` | 10,620 | 24 | 4.4 MB | One Lambda serverless price in one of 36 regions |
| `bedrock_foundation_models.csv` | 5,669 | 17 | 2.1 MB | One per-token price for one of the 53 third-party models sold through AWS Marketplace on Bedrock, in one of 35 regions |
| `bedrock_service_all.csv` | 11,657 | 35 | 5.3 MB | One per-token price for one of the 86 models Amazon bills directly on Bedrock, or one Bedrock platform feature, in one of 36 regions |
| `offer_index.json` | 269 offers | 6 fields | 0.09 MB | One AWS service that publishes a price list, with the address of its version index |
| `ec2_version_index.json` | 122 versions | 3 fields | 0.03 MB | One published version of the EC2 offer, with the dates it was in force |
| `ec2_region_index.json` | 106 regions | 2 fields | 0.02 MB | One region the current EC2 offer covers, with the address of that region's file |

**What one row represents, precisely.** In every price-list file, one row is one price: a specific product under a specific purchase term at a specific rate, in one region, on the day the file was published. The row key is `RateCode`, and it is unique in all eight files, checked file by file: 394,515 distinct rate codes in 394,515 EC2 us-east-1 rows, 369,916 in eu-west-1, 30,485 in RDS, 40,654 in SageMaker, 9,943 in S3, 10,620 in Lambda, 5,669 in the Marketplace Bedrock file and 11,657 in the Amazon-billed one. No duplicates anywhere.

`SKU` is **not** unique. It identifies a *product*, not a price. EC2 us-east-1 holds 120,646 SKUs behind 394,515 rows, because one product carries an on-demand price plus up to twenty reserved-term prices. Group by `SKU` when you want products; group by `RateCode` when you want prices.

A reserved term with an upfront fee occupies **two rows**. One has `Unit` = `Quantity` and holds the upfront dollars; its sibling has `Unit` = `Hrs` and holds the running rate, which is 0 for an All Upfront term. Any effective hourly rate must combine both.

**How the tables join.** All eight price-list files share the same eleven leading columns, so they stack. Within one file, `RateCode` is always `SKU` then `OfferTermCode` then a price-dimension code, joined by dots, on every row of `ec2_us-east-1.csv`. Across files there is no shared key: a SKU belongs to one offer, so it will not join EC2 to RDS or to either Bedrock file. Across versions of the same offer a SKU usually does carry over, but not always, so a join on SKU quietly loses the products that were retired. The safer join across files or across versions is on the product attributes (`Instance Type` plus `Operating System` plus `Tenancy` plus `CapacityStatus` plus `Pre Installed S/W` plus `TermType`, and for reserved rows the three lease columns). The index files join to the CSVs by offer code and by version stamp: `ec2_version_index.json` gives the version strings that go into the archived-file addresses, and the `Version` metadata line inside each CSV says which version you are holding.

**Coverage in time.** The eight current files are a single snapshot, not a time series. They were published between 31 August and 4 September 2026. `EffectiveDate` is the date the price came into force, not a change date: in `ec2_us-east-1.csv` it takes only two values, 2026-09-01 and 2026-09-04, and a price unchanged since 2019 still shows a 2026 date. The one exception is `bedrock_foundation_models.csv`, whose `EffectiveDate` holds four values from 2025-03-06 to 2026-09-01 and does record when each model's price last moved. Real history comes from the archived versions: 122 EC2 versions in all, the oldest effective 1 December 2015 and the newest 1 September 2026, one a month from January 2017 onward and sparser before that. Other services have their own version indexes with their own depth.

**Coverage in geography.** AWS regions, plus a handful of rows for [AWS Local Zones](https://aws.amazon.com/about-aws/global-infrastructure/localzones/) and [AWS Outposts](https://aws.amazon.com/outposts/), which are smaller AWS installations placed inside a city or a customer's own building. `ec2_us-east-1.csv` is 394,480 rows in `US East (N. Virginia)` plus 34 data-transfer rows with an empty location and one Outposts row marked `Any`; the Ireland file mirrors it, at 369,889 rows in `EU (Ireland)`. The all-region files cover 40 named locations (S3, SageMaker), 37 (Lambda), 36 (the Amazon-billed Bedrock offer) and 35 (the Marketplace Bedrock offer). The current EC2 region index lists 106 regions in all, including the two GovCloud regions. **There is no geography below the region.**

**What is in scope and what is out, by design.** In: on-demand rates, reserved rates with their lease and payment options, tiered rates with a starting and ending range, free-tier rows priced at zero, and the product attributes AWS chooses to publish for each service. Out: spot prices, which live in a different API; Savings Plans, which sit on a separate `/savingsPlan/` address; enterprise discount rates, private agreements and credits, which are per-customer and never public; and third-party marketplace software other than the Bedrock model entries.

**How records enter and leave.** A price point appears when AWS launches a product or a term in a region, and disappears when AWS stops selling it. Retired instance types drop out silently. Nothing is back-dated: the file published on a given day is the price sheet for that day, and past files are frozen. AWS publishes a new version within hours of a price change, so reporting lag is effectively zero, but the archive is versioned rather than daily, so a price that changed and changed back inside one month can be invisible.

**The columns most projects turn on.** `TermType`, `LeaseContractLength`, `PurchaseOption`, `OfferingClass`, `PricePerUnit`, `Unit`, `Region Code`, `Instance Type`, `vCPU`, `Memory`, `Physical Processor`, `Operating System`, `Tenancy`, `CapacityStatus` and `Pre Installed S/W`; plus RDS `Database Engine` and `Deployment Option`; plus Bedrock `serviceName`, `Model`, `Provider`, `Inference Type` and `service_tier`.

### 5.1 The shared price columns, in every price-list file

The first eleven of these columns start every price-list CSV, in this order, checked file by file. The remaining eight appear in most files: the three lease columns only in EC2 and RDS, where reserved terms are sold; `RelatedTo` only in EC2, RDS, SageMaker and Lambda; and `Product Family` and `serviceCode` in all but `bedrock_foundation_models.csv`. The definitions in quotation marks are Amazon's own, from [Reading the service price list file for an AWS service](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-service-price-list-file-for-services.html); everything else in the Meaning column is inferred from the data. Percent filled and distinct counts are from `ec2_us-east-1.csv` unless another file is named.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `SKU` | text, 16 characters | 100 | 120,646 | `2223RRAP6Z3VBN3N`, `5G4TA8Z4MUKE6MJB` | "A unique code for a product. Use the `SKU` code to correlate product details and pricing." Identifies the thing being sold, not the price, so it is not unique in the file. A SKU is scoped to one offer, so it never joins across services. Within EC2 us-east-1 a SKU is mostly stable over time: 3,755 of the 3,887 SKUs in the September 2018 archived file are still in the current one, and all 80,316 from the August 2025 file are. The other 132 were retired, so an inner join on SKU across versions silently drops products; count the rows you keep. |
| `OfferTermCode` | text, 10 characters | 100 | 26 | `JRTCKXETXF` on 120,543 of the 120,544 on-demand rows, `4NA7Y494T4`, `38NPMPTW36` | "A unique code for a specific type of term." AWS publishes no code list, but each of the 26 codes in this file maps to exactly one combination of lease length, payment option and offering class, checked across all 394,515 rows, so grouping the three term columns recovers the meaning. |
| `RateCode` | text | 100 | 394,515 | `5G4TA8Z4MUKE6MJB.JRTCKXETXF.6YS6EN2CT7` | "A unique code for a product, offer, and pricing-tier combination." SKU, then term code, then price dimension, joined by dots. This is the row key. |
| `TermType` | text | 100 | 2 | `OnDemand` (120,544), `Reserved` (273,971) | The purchase model. SageMaker, S3, Lambda and both Bedrock files are `OnDemand` only; EC2 and RDS carry both. Amazon's documentation says "The valid term types are `Reserved`, `OnDemand`, and `FlatRate`"; `FlatRate` appears in none of these files. |
| `PriceDescription` | text | 100 | 134,657 | `$0.634 per On Demand RHEL with SQL Web c5d.2xlarge Instance Hour`, `Upfront Fee` | Free text AWS writes for each rate. Good for a sanity check, useless as a key. Formatting is inconsistent between services. |
| `EffectiveDate` | date, `YYYY-MM-DD` | 100 | 2 in EC2, 4 in the Marketplace Bedrock file | `2026-09-01`, `2026-09-04` | "The date that a service price list file goes into effect." Not a change date in most offers. |
| `StartingRange` | integer as text | 72.17 | 1 in EC2 (`0`) | `0`, `25000000000` | Lower bound of the usage tier this price covers. Empty on every reserved upfront-fee row. S3 and Lambda use it heavily, with 8 and 5 distinct values. |
| `EndingRange` | integer or `Inf` as text | 72.17 | 2 in EC2 | `Inf` (284,710 rows), `750` | Upper bound of the tier. `Inf` is a literal string, not a number, and it will break a naive numeric cast. |
| `Unit` | text | 100 | 14 in EC2, 26 in SageMaker | `Hrs` (284,630), `Quantity` (109,804), `GB`, `1M tokens`, `1K tokens` | The billing unit. Units differ *within* one file: EC2 mixes hours, one-off quantities, gigabytes and IOPS-months. Never sum or compare prices without grouping on `Unit`. |
| `PricePerUnit` | fixed-decimal text | 100 | 121,987 | `0.1920000000`, `0.0000000000`, `13370513` | The dollar amount for one unit. Always a string with ten decimal places, except for large integers. 101,639 EC2 rows are exactly zero; see section 6. The EC2 us-east-1 range is 0 to 13,370,513, that maximum being a three-year upfront fee for a `u7in-32tb.224xlarge`. |
| `Currency` | text | 100 | 1 | `USD` | Always `USD` in every file here. |
| `RelatedTo` | text | 0.0 in EC2, 3.22 in Lambda | 1 to 3 | `R3WPVNCD34N9W7UV` | A SKU this rate depends on. Present in EC2, RDS, SageMaker and Lambda; effectively empty. Undocumented; appears to link an add-on rate to its base product. |
| `LeaseContractLength` | text | 69.45 | 4 | `1yr` (137,180), `3yr` (136,761), `1 yr` (15), `3 yr` (15) | Reserved rows only. Empty on all 120,544 on-demand rows. Four spellings for two values: `1yr` and `3yr` dominate, with 30 rows spelled with a space. Normalize before grouping. |
| `PurchaseOption` | text | 69.45 | 6 | `All Upfront`, `Partial Upfront`, `No Upfront`, `AllUpfront`, `PartialUpfront`, `NoUpfront` | Reserved rows only. Three real options in two spellings; the space-free spellings appear on 810 rows. Normalize. |
| `OfferingClass` | text | 69.45 | 2 | `standard` (139,691), `convertible` (134,280) | Reserved rows only. A convertible reservation [can be exchanged](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ri-convertible-exchange.html) for a different reservation later, and it costs more: a three-year all-upfront m5.xlarge is $2,322 convertible against $1,897 standard. RDS carries only `standard`. |
| `Product Family` | text | 100 (99.88 in RDS, 25.63 in S3) | 19 in EC2 | `Compute Instance` (356,233), `Compute Instance (bare metal)` (37,013), `Dedicated Host` (1,177), `Data Transfer` (34) | "The category for the type of product." The first filter you should write. In EC2, 393,246 of 394,515 rows are one of the two compute-instance families; the other 1,269 are storage, transfer, load balancer and fee rows that do not belong in a compute comparison. |
| `serviceCode` | text | 100 | 1 | `AmazonEC2`, `AmazonRDS`, `AWSLambda` | The offer code. Constant within a file; useful once you have stacked files. |
| `Location` | text | 99.99 (68.25 in S3) | 2 in EC2, 40 in SageMaker | `US East (N. Virginia)`, `EU (Ireland)`, `Any` | Human-readable region name. Spelling is not stable across services and eras: Ireland is `EU (Ireland)` here but `Europe (Ireland)` in some offers, and `Any` marks rates that apply everywhere. Prefer `Region Code`. |
| `Location Type` | text | 99.99 | 2 to 4 | `AWS Region`, `AWS Outposts`, `AWS Local Zone`, `Other` | What kind of place `Location` names. Filter to `AWS Region` for a clean regional comparison. |

Four more columns are shared by most files and sit at the end of the product block rather than the start:

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `usageType` | text | 100 | 9,773 in EC2 | `BoxUsage:c5d.2xlarge`, `UnusedDed:i8ge.24xlarge`, `ILC1-MP:ILC1_InputTokenCount_Global-Units` | The string that appears on a customer's actual AWS bill for this rate. This is the column that would let a price list be joined to a real cost report. Region-prefixed in the all-region files. |
| `operation` | text | 99.98 (0.09 in the Marketplace Bedrock file) | 43 in EC2 | `RunInstances:0210`, `CreateDBInstance:0005` | The API operation billed, with a four-character code that encodes the operating system and bundled software. Also appears on the bill. AWS publishes no table for the suffix codes. |
| `Region Code` | text | 99.99 | 1 in a regional file, 39 in S3 | `us-east-1`, `eu-west-1`, `ap-southeast-4` | Machine-readable region identifier. Use this, not `Location`. Absent from the archived EC2 snapshots up to and including August 2021, and present from the August 2022 one on. |
| `serviceName` | text | 100 | 1, except 53 in the Marketplace Bedrock file | `Amazon Elastic Compute Cloud`, `Claude Sonnet 4.6 (Amazon Bedrock Edition)` | Normally the display name of the service. In `bedrock_foundation_models.csv` it is instead the display name of the *model*, which makes it the most important column in that file. |

### 5.2 EC2 product attributes (`ec2_us-east-1.csv`, `ec2_eu-west-1.csv`, 93 columns)

The two EC2 files have identical column lists, verified column by column. After the shared columns above, 70 product attributes follow. Percentages are from us-east-1.

Instance shape and identity:

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Instance Type` | text | 99.98 | 1,563 | `m5.xlarge`, `c5d.2xlarge`, `u7in-32tb.224xlarge` | The instance name AWS sells. Family letter, generation number, optional feature letters, then size. |
| `Current Generation` | Yes/No | 99.98 | 2 | `Yes` (380,945), `No` (13,477) | Whether AWS still considers the type current. |
| `Instance Family` | text | 99.98 | 9 | `Memory optimized` (139,921), `General purpose` (112,951), `Compute optimized` (90,216), `Storage optimized`, `GPU instance`, `Machine Learning ASIC Instances`, `Media Accelerator Instances`, `FPGA Instances`, `Micro instances` | The workload class. |
| `Instance Family Category` | text | 99.98 | 6 | `Memory Optimized` (139,550), `General Purpose` (113,379), `Compute Optimized` (89,646), `Storage Optimized`, `Accelerated Computing`, `High-Performance Computing` | A second, coarser grouping. Absent from all eight archived snapshots checked, including the August 2025 one, and present in the current file. |
| `vCPU` | integer as text | 99.98 | 25 | `2`, `8`, `192` | Virtual CPUs, the number of processor threads the instance gets. The denominator for cost per vCPU-hour. |
| `Memory` | text with unit | 99.98 | 81 | `16 GiB`, `768 GiB`, `NA` | RAM, with the unit inside the string. In this file every populated value ends in ` GiB` except the 1,177 `Dedicated Host` rows, which read `NA`. The same column in the other files is not as tidy: RDS has five bare numbers with no unit, and SageMaker mixes ` GiB`, ` TiB`, a capitalized ` GIB` and `N/A`. Run `.unique()` on the column in the file you are using and decide how to parse it. |
| `Storage` | text | 99.98 | 167 | `EBS only`, `1 x 200 NVMe SSD`, `8 x 7500 NVMe SSD` | Attached local storage, free text describing count, size and media. |
| `Physical Processor` | text | 99.98 | 49 | `Intel Xeon 8375C (Ice Lake)` (69,663), `AWS Graviton4 Processor`, `AMD EPYC 9R14 Processor` | The chip. The column that lets you compare Amazon's own Graviton against Intel and AMD at equal vCPU. |
| `Clock Speed` | text | 98.41 | 27 | `3.4 GHz`, `Up to 3.7 GHz` | Free text, sometimes a range. |
| `Processor Architecture` | text | 99.98 | 2 | `64-bit`, `32-bit or 64-bit` | |
| `Processor Features` | text | 83.46 | 16 | `Intel AVX; Intel AVX2; Intel AVX512; Intel Turbo` | Semicolon-separated list, occasionally comma-separated in older files. |
| `Physical Cores` | integer as text | 0.30 | 19 | `96`, `36` | Populated only on dedicated-host rows. |
| `Normalization Size Factor` | number as text | 99.98 | 67 | `1`, `16`, `64`, `192` | AWS's size multiplier, used when a reservation is split across sizes within one family. |
| `ECU` | text | 99.98 | 61 | `39`, `375`, `NA` | Elastic Compute Unit, an obsolete AWS performance index. Mostly `NA` on modern types; do not build on it. |
| `Intel AVX Available`, `Intel AVX2 Available`, `Intel Turbo Available` | Yes/No | 99.98 | 2 each | `Yes`, `No` | Three separate processor-feature flags. |
| `GPU` | number as text | 4.87 | 10 | `1`, `4`, `8`, `16`, `0.125` | Count of accelerator chips. **Empty, not zero,** on the 375,300 rows with no GPU. The fractional values `0.125`, `0.25` and `0.5` appear only on the `g6f` and `gr6f` instance types, which are sold with a fraction of a GPU. |
| `GPU Memory` | text | 99.98 | 32 | `48 GB`, `192 GB`, `NA` | Accelerator memory. Populated on almost every row, because rows with no GPU hold the literal string `NA` rather than an empty field. This inconsistency with the `GPU` column is real; check for `NA`, not for null. |
| `Network Performance` | text | 99.98 | 96 | `Up to 10 Gigabit`, `100 Gigabit`, `Up to 12500 Megabit` | Free text mixing two units and an "up to" qualifier. Parsing it is a genuine cleaning task. |
| `Enhanced Networking Supported` | Yes/No | 99.98 | 2 | `Yes`, `No` | |
| `Dedicated EBS Throughput` | text | 97.54 | 107 | `Up to 2250 Mbps`, `30000 Mbps` | Guaranteed bandwidth to network-attached disks. |
| `Dedicated EBS Throughput Description` | text | 99.24 | 127 | `1750 Mbps`, `24000 Mbps` | A second, differently formatted copy of the same idea. Absent from all eight archived snapshots checked, including the August 2025 one. |
| `Instance` | text | 0.0 | 4 | `T3`, `T3A`, `T4G` | Populated only on the six CPU-credit rows. |
| `instanceSKU` | text | 17.47 | 34,461 | `8JMCWRQU7D6V9D75` | On capacity-reservation rows, the SKU of the underlying instance product. |

Purchase and licensing context, the columns that decide which rows are comparable:

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Tenancy` | text | 99.98 | 5 | `Shared` (196,647), `Dedicated` (183,456), `Host` (13,191), `Reserved` (1,020), `NA` | Whether the physical hardware is shared with other AWS customers. Dedicated costs more for the same shape. |
| `Operating System` | text | 99.98 | 7 | `Linux` (120,191), `Windows` (119,738), `RHEL` (56,588), `Red Hat Enterprise Linux with HA` (49,950), `SUSE` (40,035), `Ubuntu Pro` (7,818), `NA` | The operating system license folded into the hourly rate. The single largest source of price spread at fixed hardware. |
| `License Model` | text | 99.98 | 4 | `No License required` (381,112), `Bring your own license` (9,015), `License Included - Infrastructure` (4,187), `NA` | |
| `Pre Installed S/W` | text | 99.98 | 4 | `NA` (210,518), `SQL Std` (64,681), `SQL Web` (60,133), `SQL Ent` (59,090) | Bundled Microsoft SQL Server edition. Nearly half of all EC2 rows are SQL Server bundles; leaving them in doubles or triples an apparent average price. |
| `CapacityStatus` | text | 99.98 | 5 | `Used` (324,216), `UnusedCapacityReservation` (34,461), `AllocatedCapacityReservation` (34,460), `AllocatedHost` (1,177), `NA` | Whether the rate is for capacity you are running (`Used`) or for capacity reserved and sitting idle. Filter to `Used`. Of the 52,198 compute-instance groups formed by instance type, operating system, tenancy, pre-installed software and term type, 29,436 carry all three of `Used`, `AllocatedCapacityReservation` and `UnusedCapacityReservation`, and 22,759 carry only one, so an unfiltered count roughly triples some products and not others. |
| `MarketOption` | text | 99.98 | 2 | `OnDemand` (394,335), `CapacityBlock` (93) | [Capacity Blocks](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-capacity-blocks.html) are pre-booked windows of GPU capacity. The column first appears in the August 2022 archived snapshot; it is absent from the 2018 to 2021 ones. |
| `AvailabilityZone` | text | 99.98 | 1 | `NA` | Always `NA`. AWS does not publish list prices below the region. |
| `ClassicNetworkingSupport`, `VPCNetworkingSupport` | text | 99.98 | 2 and 1 | `false`, `true` | Legacy networking flags; `VPCNetworkingSupport` is `true` on every populated row. |
| `Product Type`, `Resource Type`, `SnapshotArchiveFeeType`, `Volume API Name`, `Storage Media`, `Volume Type`, `Max Volume Size`, `Max IOPS/volume`, `Max IOPS Burst Performance`, `Max throughput/volume`, `Provisioned`, `EBS Optimized`, `Elastic Graphics Type` | text | 0.0 to 0.01 each | 1 to 7 each | `SSD-backed`, `Provisioned IOPS`, `gp3`, `List:Snapshot` | Thirteen storage and snapshot attributes carried in the EC2 offer for its handful of non-compute rows. Each is populated on fewer than 60 rows. They are part of why the file has 93 columns. |
| `Group`, `Group Description` | text | 0.01 | 20 each | `EBS Time Based Copy Tier 1`, `Charge per Provisioned mbps` | Billing-group labels for the fee rows. |
| `Transfer Type`, `From Location`, `From Location Type`, `To Location`, `To Location Type`, `From Region Code`, `To Region Code` | text | 0.01 | 1 to 11 each | `InterRegion Outbound`, `US East (N. Virginia)`, `ap-southeast-2` | The seven columns describing the 34 data-transfer rows in this file. The price of moving data between regions lives here, and far more completely in the separate `AWSDataTransfer` offer. |
| `Instance Capacity - large`, `- medium`, `- metal`, `- xlarge`, `- 2xlarge`, `- 4xlarge`, `- 8xlarge`, `- 9xlarge`, `- 10xlarge`, `- 12xlarge`, `- 16xlarge`, `- 18xlarge`, `- 24xlarge`, `- 32xlarge` | integer as text | 0.01 to 0.17 each | 1 to 10 each | `96`, `48`, `8`, `1` | Fourteen columns, one per instance size, giving how many instances of that size fit on one dedicated host. Populated only on the 1,177 `Dedicated Host` rows. |

**Column differences in the archived versions**, checked against the current 93. The eight archived files checked are the September or August snapshot of each year from 2018 to 2025, so a column labeled below as absent in one year may have appeared at some point between two snapshots:

| Archived version | Columns | Columns absent that the current file has | Columns present that the current file lacks |
|---|---|---|---|
| 2018 | 77 | `RelatedTo`, `AvailabilityZone`, `ClassicNetworkingSupport`, `Dedicated EBS Throughput Description`, `Elastic Graphics Type`, `From Region Code`, `Instance Capacity - metal`, `Instance Family Category`, `instanceSKU`, `MarketOption`, `Product Type`, `Region Code`, `Resource Type`, `SnapshotArchiveFeeType`, `To Region Code`, `Volume API Name`, `VPCNetworkingSupport` | `Elastic GPU Type` |
| 2019 | 78 | the same list minus `Elastic Graphics Type` and `instanceSKU` | none |
| 2020 | 82 | 11 of them, including `Region Code` and `MarketOption` | none |
| 2021 | 87 | `Dedicated EBS Throughput Description`, `From Region Code`, `Instance Family Category`, `Region Code`, `SnapshotArchiveFeeType`, `To Region Code` | none |
| 2022 to 2025 | 91 | `Dedicated EBS Throughput Description`, `Instance Family Category` | none |

The practical consequence: there is no `Region Code` in any snapshot up to and including August 2021, so a stacked history has to take the region from the file name or from `Location`, and `MarketOption` and `Instance Family Category` exist for only part of the series.

### 5.3 RDS product attributes (`rds_us-east-1.csv`, 58 columns)

RDS is Amazon's managed database service: AWS runs the database software for you on an instance you rent. This file shares all nineteen leading price columns plus `usageType`, `operation`, `Region Code` and `serviceName`, leaving 35 database-specific attributes:

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Database Engine` | text | 100 | 13 | `Oracle` (6,785), `SQL Server` (5,025), `Db2` (4,537), `MySQL` (4,290), `PostgreSQL` (4,168), `MariaDB` (4,019), `Aurora PostgreSQL` (727), `Aurora MySQL` (623), four Outposts variants, `Any` | The database software. Commercial engines carry most of the rows because each edition and license model multiplies out. |
| `Database Edition` | text | 53.9 | 14 | `Enterprise`, `Standard Two`, `Advanced` | Only the commercial engines have editions. |
| `Engine Code` | text | 99.99 | 43 | `5`, `18`, `15` | AWS's numeric engine identifier, matching the suffix in `operation`. There is no published code table, but each of the 43 codes maps to exactly one `Database Engine` value, checked across every row of this file, so cross-tabulating the two columns recovers the meaning. |
| `Engine Major Version`, `Engine Media Type`, `Extended Support Pricing Year` | text | 0.09 to 6.78 | 2 to 8 | `15`, `AWS-provided`, `Year 1, Year 2` | Populated only on the extended-support surcharge rows, which price staying on an old Postgres or MySQL version after AWS stops supporting it normally. |
| `Deployment Option` | text | 99.66 | 5 | `Single-AZ` (16,102), `Multi-AZ` (13,992), `Multi-AZ (readable standbys)` (214), `Multi-AZ (SQL Server Mirror)`, `Single-AZ (Oracle RAC)` | How many availability zones the database is copied across. Multi-AZ roughly doubles the instance rate, so this must be held fixed in any comparison. |
| `Deployment Model` | text | 6.54 | 1 | `Custom` | RDS Custom rows only. |
| `Instance Type` | text | 97.85 | 415 | `db.m7i.2xlarge`, `db.r3.2xlarge` | Database instance class, always prefixed `db.`. |
| `Instance Type Family` | text | 97.85 | 49 | `R3`, `R6i`, `M8i` | |
| `Instance Family`, `vCPU`, `Memory`, `Storage`, `Network Performance`, `Physical Processor`, `Clock Speed`, `Processor Architecture`, `Processor Features`, `Current Generation`, `Normalization Size Factor`, `Dedicated EBS Throughput`, `Enhanced Networking Supported` | mixed | 4.07 to 97.93 | | `General purpose`, `8`, `61 GiB`, `EBS Only` | The same hardware attributes as EC2, same formats, same units inside strings. `Clock Speed` is populated on only 12.51 percent of rows. |
| `License Model` | text | 97.96 | 6 | `No license required`, `Bring your own license`, `License included`, `Marketplace`, `NA` | Note the lower-case spelling differs from EC2's. |
| `Unbundled Licensing` | TRUE/FALSE | 91.26 | 2 | `FALSE`, `TRUE` | Whether the license is priced separately from the instance. |
| `WindowsLicenseMultiplier` | integer as text | 1.75 | 2 | `1`, `2` | |
| `Storage Media`, `Volume Type`, `Volume Name`, `Min Volume Size`, `Max Volume Size` | text | 0.63 to 1.31 | 3 to 9 | `SSD`, `General Purpose-GP3`, `gp3`, `100 GB` | Populated on the 272 storage rows and 183 provisioned-IOPS rows. |
| `ACU`, `LimitlessPreview`, `ThroughputCapacity` | text | 0.01 each | 1 | `1`, `Yes` | Aurora Serverless and Limitless rows. Nearly empty. |
| `Group`, `Group Description` | text | 0.9 | 11 | `Aurora Backtrack`, `RDS Snapshot Size` | |

### 5.4 SageMaker product attributes (`sagemaker_all.csv`, 67 columns)

SageMaker is Amazon's managed machine-learning platform. This is an all-region file, so `Location` has 40 values and `Region Code` 39. `TermType` is `OnDemand` on every row.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Component` | text | 80.88 | 27 | `Hosting` (4,002), `Notebook` (3,471), `studio-jupyterlab` (3,421), `Training` (3,077), `Cluster` (2,904), `Processing`, `AsyncInf`, `BatchTransform`, `Spot Training` | Which part of the machine-learning workflow the rate is for. The same physical instance is priced differently for training and for hosting, and this column is what separates them. |
| `Instance Type` | text | 78.29 | 1,706 | `ml.m6i.12xlarge-BatchTransform`, `ml.inf2.48xlarge-Cluster`, `ml.t3.medium` | Usually the component glued onto the instance name with a hyphen, so this column is **not** comparable to `Instance Name` or to an EC2 instance type as it stands. Splitting on the hyphen is not a safe blanket rule: 174 of the 1,706 values, on 6,307 rows, contain no hyphen at all. Use `Instance Name` where you can, and inspect the values before splitting. |
| `Instance Name` | text | 83.16 | 539 | `ml.m5d.large`, `ml.r7i.12xlarge`, `sc.c6i.xlarge` | The clean instance identifier. Use this one rather than `Instance Type`. Two prefixes appear: 382 distinct values begin `ml.` and 157 begin `sc.`. Dropping the `ml.` prefix lines a value up with an EC2 instance type for 371 of those 382; the rest, and all the `sc.` values, do not match a type in `ec2_us-east-1.csv`. Check what your join keeps rather than assuming it is complete. |
| `PlatoInstanceName`, `PlatoInstanceType`, `PlatoClassificationType` | text | 3.21 to 78.29 | 16 to 61 | `m6i`, `Training`, `PublicTask` | Internal AWS naming that duplicates `Instance Name` and `Component`. Undocumented; the values line up with the documented columns and add nothing. |
| `Compute Type` | text | 82.75 | 5 | `Standard Instances`, `Compute Optimized Instances`, `Accelerated Computing Instances` | |
| `Physical CPU`, `Physical GPU`, `GPU`, `GPU Memory`, `V CPU`, `Memory`, `Memory(GB)`, `Storage`, `Network Performance`, `Clock Speed`, `Processor Architecture`, `Current Generation` | mixed | 0.93 to 83.21 | | `AWS Graviton2 Processor`, `NVIDIA L4`, `1`, `640`, `8`, `192 GiB` | Hardware attributes. `N/A` is used as a string for absent accelerators, and there are two memory columns and two CPU-count columns with different spellings. |
| `ModelName`, `Model Description` | text | 2.81 | 35 and 37 | `huggingface-llm-qwen2-5-14b-instruct`, `Qwen2.5 14B Instruct` | JumpStart rows: the price of running a named open-weights model on SageMaker. |
| `TokenType`, `Technique`, `PEFTType`, `DataGenerationTechniques` | text | 0.02 to 2.15 | 2 to 5 | `Prefill`, `Output`, `SFT`, `DPO`, `RLAIF`, `LORA`, `FULLRANK` | Fine-tuning and serverless-training rows. |
| `Integration Type`, `Integrating Service`, `Integrating API`, `Integrating Feature` | text | 0.16 to 2.63 | 3 each | `Bedrock Evaluation Job`, `Textract`, `AnalyzeDocument` | Rows where SageMaker calls another AWS service. |
| `Labeling Task Type`, `Workforce Type`, `Automatic Label` | text | 2.63 to 2.79 | 2 to 43 | `Semantic Segmentation`, `PublicTaskAt0.720` | Ground Truth human-labeling prices, including the per-task rate paid for public-workforce annotation. |
| `PartnerAppType`, `PartnerAppTier`, `PartnerAppResourceName`, `PartnerAppResourceService`, `PartnerAppResourceType` | text | 8.15 each | 4 to 26 | `Fiddler`, `Comet-Medium`, `EC2:m5.4xlarge`, `PA-Aurora`, `Compute` | Partner software resold inside SageMaker, with the underlying AWS resource named. |
| `Volume Type`, `Max throughput/volume`, `Storage Type`, `DataStore StorageType`, `Tracking Server Size`, `Unified Studio Compute`, `ScepterUsageType`, `Group`, `Group Description` | text | 0.09 to 6.93 | 1 to 30 | `General Purpose-Training`, `FSX Lustre SSD`, `Small`, `Unused` | Storage, experiment-tracking and feature-store rows. |

### 5.5 S3 product attributes (`s3_all.csv`, 35 columns)

S3 is Amazon's file storage service. Prices here are per gigabyte-month of storage, per thousand requests, or per gigabyte moved.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Storage Class` | text | 12.39 | 11 | `General Purpose`, `Intelligent-Tiering`, `Infrequent Access`, `Archive`, `Archive Instant Retrieval`, `Non-Critical Data`, `Vectors`, `Analytics`, `Files`, `Tags`, `High Performance` | The storage tier, and this is the complete list of its 11 values. Populated on all 911 `Storage` rows and on 321 rows whose `Product Family` is empty; the 838 `API Request` rows, 741 `Fee` rows and 58 `Data Transfer` rows all carry it empty. |
| `Volume Type` | text | 12.39 | 26 | `One Zone - Infrequent Access`, `Vectors` | A finer split than `Storage Class`; the two together identify the product. |
| `Availability`, `Durability` | text | 8.48 and 8.82 | 4 and 3 | `99.9%`, `99.5%`, `99.999999999%`, `N/A` | The service-level numbers AWS quotes for that class, as strings with a percent sign. **These are the only quality attributes anywhere in the price lists.** |
| `Fee Code`, `Fee Description` | text | 19.76 | 46 and 54 | `S3:EarlyDelete-SIA`, `Fee for Standard Retrieval of data stored from Glacier Deep Archive` | Retrieval, early-delete and select fees. |
| `Group`, `Group Description` | text | 36.1 | 60 and 100 | `S3-API-Tier8`, `INT-AA-RestoreObject`, `POST requests to Glacier` | The API request tiers. Per-request prices live here. |
| `Transfer Type`, `From Location`, `From Location Type`, `From Region Code`, `To Location`, `To Location Type`, `To Region Code` | text | 29.49 to 31.75 | 3 to 51 | `InterRegion Outbound`, `Europe (Spain)`, `ap-southeast-2` | Data-transfer rows, 3,157 of them, giving the price of moving a gigabyte between region pairs. `From Location` mixes region names with two-letter country codes such as `ZA` and `AU` on some rows. |
| `Overhead` | text | 0.7 | 2 | `Staging Storage`, `Staging Storage 1` | |

### 5.6 Lambda product attributes (`lambda_all.csv`, 24 columns)

Lambda runs a piece of code on demand and bills for the time it runs. This is the narrowest file. `Product Family` is `Serverless` on all 10,620 rows.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Group` | text | 9.11 | 30 | `AWS-Lambda-Duration`, `AWS-Lambda-Duration-ARM`, `AWS-Lambda-Requests`, `AWS-Lambda-Provisioned-Concurrency`, `AWS-Lambda-SnapStart-Restore`, `AWS-Lambda-Durable-Execution-Operations` | The billing dimension. Only 968 rows carry it; the rest are the managed-instance rows below. The paired x86 and ARM values here are the cleanest place in the whole dataset to see two chip architectures priced on the same billing dimension. |
| `Group Description` | text | 9.11 | 28 | `Invocation call for a Lambda function`, `Invocation duration weighted by memory assigned to function, measured in GB-s` | A plain-English definition of the dimension. |
| `Lambda Managed Instance Type` | text | 90.32 | 483 | `m6a.32xlarge`, `m7g.large`, `c5ad.16xlarge` | Lambda now also sells whole EC2-shaped instances. These 9,592 rows name an EC2 instance type directly. |
| `Lambda Managed Instances - Request Type` | text | 0.56 | 2 | `Request`, `Request-ARM` | |
| `operation` | text | 0.0 | 0 | empty | Present but completely empty in this file. |

### 5.7 Bedrock Marketplace models (`bedrock_foundation_models.csv`, 17 columns)

Bedrock is Amazon's service for calling large language models by the token. This file holds the 53 models that AWS bills through its Marketplace, essentially Anthropic, Cohere, TwelveLabs, Stability, AI21, Writer, Luma and Meta Llama 2. It carries only the shared price columns plus `Location`, `Location Type`, `usageType`, `operation`, `Region Code` and `serviceName`. **There are no product-attribute columns at all,** so everything you know about a row comes from three fields.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `serviceName` | text | 100 | 53 | `Claude Sonnet 4.6 (Amazon Bedrock Edition)` (620 rows), `Claude Sonnet 4.5 (Amazon Bedrock Edition)` (553), `Cohere Embed 4 Model (Amazon Bedrock Edition)`, `TwelveLabs Pegasus 1.2 (Amazon Bedrock Edition)`, `Meta Llama 2 Chat 70B (Amazon Bedrock Edition)` | The model. There is no separate family or version field, so a family and generation have to be parsed out of this string. |
| `PriceDescription` | text | 100 | 1,738 | `AWS Marketplace software usage\|us-east-1\|Million Input Tokens`, `...\|Cache Read Tokens - Standard, Global`, `...\|Provisioned Throughput Hourly Price (6 Months Commit)`, `...\|Million batch input tokens` | Pipe-delimited: a fixed prefix, then the region, then the price dimension. **This is the only place the price dimension is recorded in this file.** Input against output, cached against uncached, batch against standard, and the commitment length are all buried in this string and must be parsed out. |
| `Unit` | text | 100 | 12 | `1M tokens` (4,274), `1M TPM Hour` (1,036), `hour` (206), `seconds`, `Input Images`, `image`, `Model/month`, `Images Processed`, `Text Requests`, `Search Units`, `Training Tokens`, `Embeddings` | Note that this file quotes per **million** tokens while the file in 5.8 quotes per **thousand**. |
| `PricePerUnit` | fixed-decimal text | 100 | 186 | `5.0000000000`, `0.5000000000`, `0.0000000200` | Range 0.00000002 to 267. |
| `EffectiveDate` | date | 100 | 4 | `2025-03-06`, `2026-07-01`, `2026-08-01`, `2026-09-01` | Unlike every other offer here, this one carries a meaningful change date. |
| `Region Code` | text | 100 | 35 | `us-east-1` (394 rows), `us-west-2` (372), `eu-central-1`, `ap-northeast-1` | Every model is priced separately in every region it is offered in. |
| `usageType` | text | 100 | 1,240 | `ILC1-MP:ILC1_InputTokenCount_Global-Units`, `APS3-MP:APS3_cache_read_tokens_global_standard-Units` | A second, machine-readable encoding of the same price dimension, with a region prefix. Easier to parse than `PriceDescription` once you learn the prefixes. |
| `operation` | text | 0.09 | 1 | `Usage` | Nearly empty. |

### 5.8 Amazon Bedrock service (`bedrock_service_all.csv`, 35 columns)

The 86 models Amazon bills directly, including all the Nova models, Grok, Qwen, DeepSeek, GLM, Kimi, Nemotron and gpt-oss, plus the Bedrock platform features. **This is a different file from 5.7 with a different schema, and the two together are the whole Bedrock price sheet.** This one has real attribute columns, so it is easier to work with.

| Column | Type | Percent filled | Distinct | Example values | Meaning |
|---|---|---|---|---|---|
| `Model` | text | 92.78 | 86 | `Nova 2.0 Omni` (788 rows), `xai.grok-4.6` (648), `Nova 2.0 Pro`, `gpt-oss-120b`, `GLM 5`, `DeepSeek v3.2`, `Qwen3 Coder Next`, `Kimi K2.5`, `NVIDIA Nemotron Nano 2`, `Devstral` | The model name. Naming is inconsistent: some entries are display names, some are API identifiers with a vendor prefix. |
| `Provider` | text | 63.8 | 14 | `Mistral` (1,284), `Qwen` (1,268), `Nvidia` (864), `OpenAI` (816), `Google` (647), `Z AI`, `Minimax AI`, `DeepSeek`, `Moonshot AI`, `Writer`, `Mistral AI`, `Meta`, `Kimi AI`, `Anthropic` | The company that made the model. Note that `Mistral` and `Mistral AI` are two spellings of one vendor, and Amazon's own Nova models leave it empty. |
| `Inference Type` | text | 86.89 | 60 | `Input tokens` (1,549), `Output tokens` (1,477), `Output tokens flex`, `Input tokens priority`, `output tokens batch`, `Input Image Token Count`, `Prompt cache write input tokens` | The price dimension, spelled out as a column rather than buried in text. This is what the file in 5.7 lacks. Capitalization is inconsistent. |
| `service_tier` | text | 41.39 | 7 | `standard`, `flex`, `global-priority` | The latency and priority tier, which changes the token price for the same model. |
| `Feature` | text | 43.66 | 31 | `On-demand Inference` (3,841), `Batch Inference` (731), `Model Customization`, `Custom Model Import`, `Provisioned Throughput Inference - 1 month`, `Flow Execution`, `Reranker` | Which Bedrock capability the rate belongs to. |
| `Feature Type` | text | 1.42 | 5 | `Inference`, `Training`, `Prompt cache read` | |
| `Batch` | TRUE/FALSE | 0.17 | 2 | `True`, `False` | Redundant with the batch values inside `Inference Type`. |
| `Modality` | text | 0.17 | 5 | `Video`, `Audio`, `Document image` | |
| `Token Type` | text | 6.54 | 8 | `Cache Read Input Tokens`, `input-tokens-long-ctx`, `cache-write-tokens-30m` | Long-context and cache-window variants. Two naming conventions in one column. |
| `Architecture`, `Architecture Name`, `Custom Model Unit Version` | text | 0.55 | 2 to 10 | `Qwen2VL`, `Mistral`, `GPT_BigCode`, `v1.0` | Custom Model Import rows: the price of bringing your own model weights depends on the base architecture. |
| `Model Unit`, `Titan Model`, `Titan Model Unit` | text | 0.28 to 1.92 | 7 to 11 | `Nova Lite`, `Titan Text G1 Lite`, `Titan Image Generator G1` | Provisioned-throughput model units, with a separate pair of legacy Titan columns. |
| `Policy Type` | text | 1.76 | 15 | `GuardrailContent`, `ContextualGrounding`, `GuardrailSensitiveInfoChecks` | Guardrails rows, priced per text unit. |
| `Unit` | text | 100 | 23 | `1K tokens` (10,736), `TextUnit`, `hour`, `1M tokens`, `image`, `Minutes Processed`, `Pages Processed` | Mostly per **thousand** tokens here, against per **million** in 5.7. Convert before comparing the two files. |

### 5.9 The index files

`ec2_version_index.json` and `aws_offer_index.csv` in `sample/` are the flattened forms of two of the three JSON index files, so you can look at them without writing any JSON code.

| File | Key | Fields | Meaning |
|---|---|---|---|
| `offer_index.json` | `offerCode`, 269 of them, for example `AmazonEC2`, `A4B`, `ACM` | `versionIndexUrl`, `currentVersionUrl`, `currentRegionIndexUrl` on all 269; `savingsPlanVersionIndexUrl` and `currentSavingsPlanIndexUrl` on only 15 of them, including `AmazonEC2`, `AmazonRDS`, `AmazonECS`, `AmazonEKS` and `AmazonSageMaker` | Every AWS service that publishes a price list, with the address of that service's version index and current file. The path fragments are relative to the endpoint host, [pricing.us-east-1.amazonaws.com](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json). |
| `ec2_version_index.json` | `version`, 122 of them, for example `20180910235641` | `versionEffectiveBeginDate`, `versionEffectiveEndDate`, `offerVersionUrl` | Every published version of the EC2 offer, with the dates it was in force. The newest version has an empty end date. Not sorted by date. |
| `ec2_region_index.json` | `regionCode`, 106 of them, for example `us-east-1` | `currentVersionUrl` | Every region the current EC2 offer covers, including `us-gov-west-1` and `us-gov-east-1`. No China region appears in this index. |

### 5.10 Code tables

**`TermType` and the reserved term columns, EC2 us-east-1.** 120,544 rows are `OnDemand` with the three lease columns empty. The remaining 273,971 reserved rows split as follows, after normalizing the spelling variants:

| Lease | Purchase option | Offering class | Rows |
|---|---|---|---|
| 3yr | All Upfront | standard | 28,070 |
| 3yr | Partial Upfront | standard | 28,070 |
| 1yr | All Upfront | standard | 28,022 |
| 1yr | Partial Upfront | standard | 28,022 |
| 1yr and 3yr | All, Partial and No Upfront | convertible | 134,280 in total, 26,856 per All or Partial cell and 13,428 per No Upfront cell |
| 1yr | No Upfront | standard | 14,011 |
| 3yr | No Upfront | standard | 13,496 |

**How the two reserved rows combine, worked through for one product.** m5.xlarge, Linux, shared tenancy, `CapacityStatus` = `Used`, no pre-installed software, us-east-1, September 2026. The effective hourly rate divides the upfront fee by 8,760 hours for a one-year term or 26,280 hours for a three-year term and adds the hourly rate:

| Term | Upfront (`Unit` = `Quantity`) | Hourly (`Unit` = `Hrs`) | Effective $ per hour over the term | Discount against on demand |
|---|---|---|---|---|
| On demand | none | 0.1920 | 0.1920 | not applicable |
| 1yr No Upfront standard | 0 | 0.1210 | 0.1210 | 37% |
| 1yr Partial Upfront standard | 505 | 0.0580 | 0.1156 | 40% |
| 1yr All Upfront standard | 989 | 0.0000 | 0.1129 | 41% |
| 3yr No Upfront standard | 0 | 0.0830 | 0.0830 | 57% |
| 3yr Partial Upfront standard | 1,009 | 0.0380 | 0.0764 | 60% |
| 3yr All Upfront standard | 1,897 | 0.0000 | 0.0722 | 62% |
| 3yr All Upfront convertible | 2,322 | 0.0000 | 0.0884 | 54% |

AWS does not publish a canonical formula for the effective rate, so state the hours convention you used whenever you report one.

**`Operating System` in EC2 us-east-1**: Linux 120,191, Windows 119,738, RHEL 56,588, Red Hat Enterprise Linux with HA 49,950, SUSE 40,035, Ubuntu Pro 7,818, `NA` 108.

**`Instance Family` in EC2 us-east-1**: Memory optimized 139,921, General purpose 112,951, Compute optimized 90,216, Storage optimized 31,285, GPU instance 17,072, Machine Learning ASIC Instances 2,277, Media Accelerator Instances 452, FPGA Instances 197, Micro instances 51.

**`Physical Processor`, most common values in EC2 us-east-1**, spelled exactly as the column holds them: Intel Xeon 8375C (Ice Lake) 69,663, Intel Xeon Scalable (Sapphire Rapids) 30,308, Intel Xeon Scalable (Granite Rapids) 30,072, Intel Xeon Platinum 8259 (Cascade Lake) 29,957, AMD EPYC 7R13 Processor 28,179, Intel Xeon Platinum 8175 24,328, AMD EPYC 9R14 Processor 19,731, AMD EPYC 7571 18,444, AWS Graviton2 Processor 18,153, AWS Graviton4 Processor 13,787, AWS Graviton3 Processor 12,869. 49 distinct values in all.

**`Unit` in EC2 us-east-1**, 14 distinct values: Hrs 284,630, Quantity 109,804, GB 49, GB-Mo 11, vCPU-Hours 6, IOPS-Mo 5, LCU-Hrs 2, SnapshotAPIUnits 2, then Gbps-hrs, GB-month, GiBps-mo, IOs, Requests and hours with one row each.

**Bedrock models by file.** The Marketplace file (5.7) holds 53 models, 28 of them Claude models, led by Claude Sonnet 4.6 (620 rows across 33 regions), Claude Sonnet 4.5 (553, 35) and Claude Haiku 4.5 (541, 33), with Cohere, TwelveLabs, Stability, AI21, Writer, Luma and Meta Llama 2 behind them. The Amazon-billed file (5.8) holds 86 models led by Nova 2.0 Omni (788 rows), xai.grok-4.6 (648), Nova 2.0 Pro (622), Nova 2.0 Lite (556) and Nova Pro (302), with the Qwen, DeepSeek, GLM, MiniMax, Kimi, Nemotron, gpt-oss and Mistral families behind them.

---

## 6. Notes

### Watch out for

- **AWS says its own pricing pages, not these files, are what it charges.** On [Calling AWS services and prices using the AWS Price List](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html) Amazon writes: "The Price List Query API and Price List Bulk API provide pricing details for informational purposes only. If there's a difference between the price list file and a service pricing page, AWS charges the prices on the *service pricing page*." So a disagreement between a number here and a number on an AWS pricing page is not necessarily an error in your code, and this file is not the authority on it. Say which file and version any published number came from.
- **The five metadata lines above the header.** Every price-list CSV has five metadata lines, then the header on line 6, then data from line 7. Pass `skiprows=5` to `pd.read_csv`. Forget it and the file parses as a two-column table of nonsense. The sample files in this repository already have those lines removed, so they need no `skiprows`; the downloaded files all need it.
- **Pandas turns the literal string `NA` into a missing value.** Many columns here use `NA` to mean "does not apply", and pandas treats that text as missing by default, even with `dtype=str`. Without `keep_default_na=False`, a filter on `Pre Installed S/W == "NA"` matches zero rows instead of the correct 210,518. Always pass `keep_default_na=False` when you read these files.
- **The all-region address is 6 GB.** On 5 September 2026 the server reported `.../AmazonEC2/current/index.csv` as 5,957,234,980 bytes, which will not open on a laptop. The address with a region in it, `.../AmazonEC2/current/us-east-1/index.csv`, was 303 MB on the same day and is the one to use. There are 106 EC2 regions and the region index lists them all. The all-region RDS file has the same problem at 341 MB against 18 MB.
- **A seventh column decides whether you see the Windows premium at all: `License Model`.** Windows rows come in three license models, and only one of them prices the license. For an m5.xlarge in us-east-1 on 4 September 2026, the `No License required` Windows row is $0.3760 per hour, while the `Bring your own license` row and the `License Included - Infrastructure` row are both $0.1920, the same as Linux. Take a minimum or a median across all Windows rows and the Windows premium comes out at exactly 1.00, which is wrong. Holding `License Model` to `No License required` gives a median Windows-to-Linux ratio of 1.66 across the 852 instance types that have both. The naming is counterintuitive, so read `License Model` before you compute anything about operating system prices.
- **Six filters make EC2 rows comparable, and dropping any one changes every average.** Hold `Product Family` = `Compute Instance`, `TermType` = `OnDemand`, `Operating System` = `Linux`, `Tenancy` = `Shared`, `CapacityStatus` = `Used` and `Pre Installed S/W` = `NA`. That is 1,251 rows out of 394,515, covering 1,245 instance types. The same machine appears many times under different operating systems and capacity states, so an unfiltered average is meaningless.
- **List prices for existing EC2 instance types almost never change.** Of the 138 instance types sold on demand for Linux in us-east-1 in both the September 2018 archived file and the 4 September 2026 file, all 138 carry exactly the same price in both. m5.xlarge is $0.1920 per hour in all eight archived snapshots checked and in the current file; c5.xlarge $0.1700; r5.xlarge $0.2520; p3.2xlarge $3.0600. What changes is the catalog, from 140 on-demand Linux types in the 2018 file to 1,389 now. Anything that measures the price of a *fixed* instance over time will draw a flat line; whatever you measure has to account for a catalog that grows.
- **Cost per vCPU-hour does not fall steadily with each new instance generation.** It is often said that it does. In the 4 September 2026 us-east-1 download, the cheapest on-demand Linux rate per vCPU-hour falls to the sixth generation and then rises again: for the m family, m6 $0.0385, m7 $0.0408, m8 $0.04488, m9 $0.04892; for the c family, c6 $0.0340 rising to c9 $0.04347; for the r family, r6 $0.0504 rising to r9 $0.06421. Newer generations bring faster chips, more memory bandwidth and better networking, none of which this file measures, so a chart of dollars per vCPU per hour by generation does not show what people expect it to show.
- **Only two EC2 regions are in this download.** `us-east-1` and `eu-west-1`. Any statement about which region is cheapest overall needs more of them, and each additional regional EC2 file is another 100 to 300 MB from the region index. Plan the disk space and the download time before you widen the comparison, and do not generalize from two regions.
- **The `aws pricing` command line and SDK route is a different thing and needs credentials.** The eleven addresses in section 4 are plain public downloads. The `DescribeServices`, `ListPriceLists` and `GetPriceListFileUrl` operations shown in [Getting price list files using the AWS Price List Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api.html) sit behind `api.pricing.us-east-1.amazonaws.com` and, as that page says, need an IAM identity with permission. Those operations hand back the same `pricing.us-east-1.amazonaws.com/offers/v1.0/...` URLs this document already gives you, so there is nothing to gain by setting up an AWS account for this project.
- **`PricePerUnit` is exactly zero on 101,639 EC2 rows, 26 percent of the file.** 54,902 are the hourly component of an All Upfront reservation, where the whole cost sits in the sibling `Quantity` row; 46,723 are on-demand hourly rows priced at zero; 13 are zero-priced data-transfer rows and one is a NAT gateway row. Never treat these as bad data and never average them in blindly.
- **A reserved term is two rows, not one.** One `Quantity` row for the upfront fee and one `Hrs` row for the running rate, which is 0 for All Upfront. Any effective hourly rate must pair them on SKU and offer term code. A random sample of rows will usually break the pair, which is why the sample files cannot support this calculation.
- **`EndingRange` holds the literal string `Inf`** on 284,710 EC2 rows. `pd.to_numeric` turns it into positive infinity, `int()` raises an error, and a SQL cast fails. Handle it explicitly.
- **Coded columns have spelling variants.** `LeaseContractLength` has four spellings for two values (`1yr`, `3yr`, `1 yr`, `3 yr`), with 30 rows using the spaced form; `PurchaseOption` has six for three (`All Upfront` and `AllUpfront`, and so on), with 810 rows using the space-free form. RDS spells its license values in lower case where EC2 uses upper case. `Location` names drift between offers and eras. Normalize every coded column before grouping, and check your group counts against the file total.
- **Two conventions for "not applicable" in the same file.** `GPU` is empty on rows with no GPU, but `GPU Memory`, `ECU`, `Tenancy`, `Operating System` and `Processor Architecture` all use the literal string `NA`, and SageMaker uses `N/A` with a slash. A null check will miss most of them.
- **Units live inside strings.** `Memory` is `16 GiB`, `Network Performance` is `Up to 12500 Megabit` or `100 Gigabit`, mixing two scales with an "up to" qualifier, `Clock Speed` is `Up to 3.7 GHz`, `Availability` is `99.9%`. Everything needs parsing, and `Network Performance` alone has 96 distinct free-text values.
- **The two Bedrock files are two different schemas for the same market.** `bedrock_foundation_models.csv` has no attribute columns and hides the price dimension inside a pipe-delimited `PriceDescription`; `bedrock_service_all.csv` spells it out in `Inference Type`. One quotes per million tokens, the other per thousand. Anything covering Bedrock has to reconcile both.
- **`serviceName` means two different things.** In every file except `bedrock_foundation_models.csv` it is the service display name and is constant. In that one file it is the model name and carries 53 values.
- **`EffectiveDate` is not a change date** in EC2, RDS, SageMaker, S3, Lambda or the Amazon-billed Bedrock file. In those six it takes one or two values, all inside the current publication window. Only `bedrock_foundation_models.csv` uses it meaningfully, with four values from 2025-03-06 to 2026-09-01.
- **Columns drift across versions.** The 2018 EC2 file has 77 columns and a since-removed `Elastic GPU Type`; the current one has 93. Across the eight archived snapshots checked, `Region Code` first appears in the August 2022 file, `MarketOption` in the same one, and `Instance Family Category` and `Dedicated EBS Throughput Description` in none of them, only in the current file. Do not assume a fixed layout: stack archived files with `pd.concat(..., sort=False)`, which unions on column name and leaves a cell empty where a version had no such column.
- **The history sample in this repository is eight annual snapshots, not the whole archive.** `sample/ec2_us-east-1_history_sample.csv` holds 800 rows from each of eight archived EC2 us-east-1 files, one per year from 2018 to 2025. The version index lists 122 published versions. A monthly series means downloading more archived files yourself with the recipe above, and those files run from 33 MB for the 2018 one to 258 MB for the 2025 one, so a full decade of monthly EC2 files is far more than a laptop should hold. Pick the snapshots your question needs before you start downloading.
- **A SKU usually survives across versions, but not always.** Of the 3,887 SKUs in the September 2018 EC2 us-east-1 file, 3,755 are still in the 4 September 2026 file and 132 are gone; from the August 2025 file all 80,316 survive. A price history built as an inner join on SKU therefore drops retired products without saying so. Join on the product attributes instead, or count what your join keeps.
- **`current` is not a fixed file.** Re-download next week and you may hold a different version, with different numbers. Record the `Version` metadata line from line 4 of every file beside any number you report. An archived version, by contrast, is addressed by its own version stamp: the September 2018 file was the same size on the server on 5 September 2026 as when it was downloaded the day before.
- **`Location` is empty on 34 EC2 rows** and is `Any` on one. `Region Code` is the safer filter.
- **The two EC2 regional files stack without work**, with byte-identical column lists and identical publication stamps. That is not guaranteed for older regions or older versions.
- **Few encoding traps, but empty fields are written two ways.** All eight files are valid UTF-8 with LF line endings, no carriage returns and no byte-order mark, and non-empty fields are quoted. Empty fields are not consistent: most are written as nothing at all between two commas, while a few are written as an empty pair of quotes. A parser that treats `""` and nothing as the same value is safe; one that does not is not. Prices are USD only, with `Currency` constant.

### What the data does not contain

- **What anyone actually paid.** Every number is a list price. Negotiated private pricing agreements, credits and startup programs are confidential and appear nowhere. A claim about what a company really spends needs that company's own billing records.
- **Spot prices.** Amazon states the exclusion itself on [Calling AWS services and prices using the AWS Price List](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html): "this catalog doesn't include Amazon Elastic Compute Cloud (Amazon EC2) Spot Instances." The capacity-driven market that much cost-optimization work targets comes from a different AWS interface.
- **Savings Plans.** [Savings Plans](https://aws.amazon.com/savingsplans/) sit on a separate `/savingsPlan/` address on the same endpoint, documented in [Getting price list files manually](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-the-aws-price-list-bulk-api-fetching-price-list-files-manually.html), and are not in these files. Only 15 of the 269 offers in the service index carry savings-plan addresses at all.
- **Any quantity, usage or revenue.** There is no measure of how many instances exist, how many are sold, how much AWS earns, or which products are popular. These files are a catalog, not a transaction log.
- **Competitor prices.** No Microsoft Azure, no Google Cloud, no Oracle Cloud. Those clouds publish their prices separately, in their own formats, and instance shapes do not line up one to one, so bringing one in is a data-integration project of its own.
- **Performance.** Except for the S3 `Availability` and `Durability` strings, nothing here says how fast anything is. `vCPU`, `Memory` and `Network Performance` are specifications, not measurements, and `ECU` is an obsolete index that reads `NA` on modern types. Independent benchmark results would have to come from a hardware-benchmarking organization.
- **Capacity and availability.** Whether an instance type can actually be launched in a region on a given day, and whether a GPU family is sold out, is not here. A type can be listed and unobtainable.
- **Time-limited free tier offers.** The same AWS page says the catalog "includes perpetual free offers from AWS Free Tier. This includes usage-based free tier offers that refresh periodically, available permanently. This catalog doesn't include time-limited Free Tier offers that expire based on how long the account's been active." So the zero-priced rows are the permanent free offers only, and a new account's first-year allowances are not represented here at all.
- **Any customer, contract, account or person.** No identities of any kind appear in these files.
- **Continuous history.** The archive is versioned, not daily. A price that changed and reverted between two published versions leaves no trace at all.
- **`FlatRate` priced products.** Amazon's [Reading the service price list file for an AWS service](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-service-price-list-file-for-services.html) documents a third term type alongside `OnDemand` and `Reserved`, called `FlatRate`, with its own structure of plans, features and usage quotas. No row in any of the eight files this document covers carries it, and the columns that structure would need are not in these files either. If AWS starts publishing flat-rate plans for a service, a file downloaded later could carry rows this data dictionary does not describe; that has not happened in the files described here, checked on 4 and 5 September 2026.
- **Version history for other services, unless you fetch it.** All 269 offers have a version index at `.../{serviceCode}/index.json`, but only EC2's is in the download table here. How far back each of the others reaches varies by service, and you read it from that service's own version index.
- **Why a price is what it is.** No costs, no margins, no capacity plans, no competitive reasoning. The files record the outcome of a pricing decision and nothing about the decision. A gap between two regions is a single number with no breakdown behind it, and nothing here says what drives it.
- **Anything below the region.** `AvailabilityZone` is the literal string `NA` on every EC2 compute row. AWS does not publish per-zone list prices.
- **Any experiment or counterfactual.** These files hold one list price per product per region, with no treatment and no control group anywhere in them. This data supports comparison, not causal claims. You can say that Ireland list prices for the same instance run above Northern Virginia, or that a three-year all-upfront reservation on an m5.xlarge is listed 62 percent below its on-demand rate. None of that says why, and "moving to region X would save Y percent" is arithmetic about a hypothetical fleet, not an estimate of an effect on any real bill.
