# Morning refresh instructions

These are the steps the daily morning refresh follows. A person can follow them too.

## The site in one paragraph

Radelaide.Digital ("Tech news from the Festival State.") is a news roundup of
**digital transformation** in Adelaide and South Australia. The pages are plain
HTML generated from `data/stories.json` by `scripts/build.py`. Never hand-edit
the `.html` files; edit the JSON and rebuild.

## Categories (the `category` field)

| value        | desk                  | covers |
|--------------|-----------------------|--------|
| `government` | Government Services   | SA public sector digital services, AI policy, gov IT, cyber, digital funding |
| `health`     | Digital Health        | SA Health records, virtual care, telehealth, ambulance and hospital systems |
| `education`  | Education & Skills    | Digital and AI in SA schools, TAFE, universities, digital skills |
| `business`   | Business & Industry   | Programs, grants and advice helping SA businesses go digital or adopt AI |
| `cities`     | Smart Cities & Data   | Council digital projects, digital twins, sensors, open data in SA |

## Steps

1. Search the web for South Australian digital transformation news published in the
   **last few days** (and anything from the last 3 months not already in the file).
   Good places: SA Government and Premier media releases, ai.sa.gov.au, SA Health,
   Department for Education, business.sa.gov.au, InDaily, ABC Adelaide, iTnews,
   GovTech Review, Pulse+IT, Healthcare IT News, council newsrooms.
2. Only add a story if **all** of these are true:
   - It is genuinely about Adelaide or South Australia (or a national change with a
     clear SA angle) and fits one of the five categories.
   - You can confirm the publication date, and it is within the last 92 days.
   - It is not already in `data/stories.json` (check the URL and headline).
   - The link goes to the original publisher's article, not an aggregator, where possible.
3. Write each new entry in this format, with a summary in your own words
   (two sentences, factual, no hype, nothing the source does not say):

   ```json
   {
     "date": "YYYY-MM-DD",
     "category": "government",
     "headline": "Short, plain-English headline",
     "summary": "Two sentences in your own words.",
     "source": "Publisher name",
     "url": "https://..."
   }
   ```

   If only the month is known, use the first of the month and add
   `"date_label": "Oct 2026"`. If the date is for an event, add a label like
   `"date_label": "17–21 Aug 2026"`.
4. Remove entries older than 92 days from `data/stories.json` (the build hides
   them anyway, this just keeps the file tidy).
5. Run `python3 scripts/build.py` from the repository root.
6. Commit and push to `main`, even if there are no new stories (the "Last updated"
   date and the 3-month window still change). Use a message like
   `Morning refresh: 2 new stories`.

## Rules

- Never invent stories, dates, numbers or quotes. If you are not sure, leave it out.
- No personal information about the site owner anywhere on the site or in commits.
- Do not change the design, name, tagline or categories during a refresh.
