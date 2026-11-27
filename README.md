# Jev on the SEC firehose

Extracting data from thousands of contracts with a cheap, fast model.

A six-minute live demo by Alexander Galea at [AI Tinkerers Toronto](https://toronto.aitinkerers.org), November 2026 Meetup: Legal Tech with Clio, on November 26, 2026.

- **Notebook:** [`demo.ipynb`](demo.ipynb), the code run live on stage
- **Slides:** [`slides.pdf`](slides.pdf)
- **Event:** [AI Tinkerers Toronto November 2026 Meetup: Legal Tech with Clio](https://toronto.aitinkerers.org/p/ai-tinkerers-toronto-november-2026-meetup-legal-tech-with-clio)
- **Community:** [AI Tinkerers Toronto](https://toronto.aitinkerers.org)
- **Alexander Galea:** [zazencodes.com](https://zazencodes.com) · [LinkedIn](https://www.linkedin.com/in/alexandergalea/)

## Slides

![Title slide: Jev on the SEC firehose. Extracting data from thousands of contracts with a cheap, fast model. Alexander Galea, AI Tinkerers Toronto.](assets/slides/slide-001.webp)

![The problem: we want the same piece of data from thousands of contracts. US public companies publish about 2,300 contracts a month. Nobody can read them all. A big model like GPT can, but it is slow and expensive.](assets/slides/slide-002.webp)

![Why Jev helps: Jev answers a question about a document with one number, and it is cheap enough to run on every contract. Estimate for one month, not measured: GPT-6.2 Astra about $225 and 6 hours, Jev about $1 and 15 minutes.](assets/slides/slide-003.webp)

![The use case: imagine you work at an investment firm. You want every new contract with a clause that kicks in when the company is sold. Example: a consulting agreement where, if the company is sold, the consultant can quit and collect CDN$750,000. A buyer inherits that bill, so it changes what the company is worth. Jev scores every contract and you read only the high scores.](assets/slides/slide-004.webp)

![Jev answers with a number: given Nexstar's employment contract and the question "Can a buyout trigger consent, termination, or changed terms?", Jev answers 0.60, the probability of yes.](assets/slides/slide-005.webp)

![Numbers sort into a queue: Nexstar 60%, review. FirstEnergy 7%, skip. Planet Green 6%, skip. Example cutoff of 50% on the change-of-control flag, from a rehearsal run.](assets/slides/slide-006.webp)

![Live demo, nvb demo.ipynb: 1. Ask one question about one contract. 2. Check Jev and GPT against lawyers' labels. 3. Run every contract, live. Data: SEC EDGAR and CUAD v1, The Atticus Project, CC BY 4.0.](assets/slides/slide-007.webp)

![The pattern: Jev screens every contract. The big model reads only the flagged ones.](assets/slides/slide-008.webp)

![Alexander Galea, zazencodes.com, course: Agentic Coding Fundamentals, with a QR code to connect on LinkedIn.](assets/slides/slide-009.webp)

## Run the notebook

The notebook puts the same contracts and the same question to Jev and to an OpenAI GPT model. You need a TypeSafe API key and an OpenAI API key, and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
git clone https://github.com/zazencodes/jev-sec-firehose-talk.git
cd jev-sec-firehose-talk
export TYPESAFE_API_KEY=your_typesafe_key OPENAI_API_KEY=your_openai_key
uv run --with jupyterlab --with openai --with typesafe-sdk --with pydantic jupyter lab demo.ipynb
```

`LLM_MODEL` on line 3 of the first cell picks the GPT model. The big run in section 3 stops each model when it reaches `SPEND_LIMIT`.

## What's in this repo

| Path | What it is |
|---|---|
| [`demo.ipynb`](demo.ipynb) | The live demo |
| [`slides.pdf`](slides.pdf) | The slides, also as images in [`assets/slides/`](assets/slides) |
| [`edgar.py`](edgar.py) | Downloads the Exhibit 10 contracts attached to a month of 8-K filings on SEC EDGAR |
| [`data/exhibits/`](data/exhibits) | 750 contracts filed in November 2026, one file per filing day |
| [`data/cuad-sample.json`](data/cuad-sample.json) | Eight CUAD contracts with lawyers' labels for change of control, non-compete and uncapped liability |
| [`prepare_cuad.py`](prepare_cuad.py) | Rebuilds the CUAD sample |

The contracts come from [SEC EDGAR](https://www.sec.gov/edgar/search/). The labeled sample comes from [CUAD v1](https://huggingface.co/datasets/theatticusproject/cuad) by The Atticus Project, licensed CC BY 4.0.
