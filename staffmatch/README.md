# StaffMatch — AI matchmaking for restaurant hiring

## The problem

Every restaurant operator lives the same loop: you're always hiring, and the people
you find never quite fit. Restaurant labor is deceptively specific —

- **Skills are niche.** A "line cook" who's great at a high-volume flat-top brunch
  station is not the same hire as a saucier from a tasting-menu kitchen. A bartender
  who can run a 300-cover sports bar is not a craft-cocktail bartender.
- **Schedules are jagged.** Availability is per-day, per-daypart, and changes weekly.
  A perfect-skills candidate who can't work Friday dinner is not a match.
- **Pay requirements are individual.** Base wage vs. tip structure vs. guaranteed
  hours — each candidate weighs these differently.
- **History matters.** Tenure patterns, the caliber of past kitchens, references,
  background checks — the signal is in the details, not the job title.

Generic job boards match on titles and keywords. Shift marketplaces match on
"warm body, right place, right time." Neither models the person.

## The idea

A matchmaking platform that:

1. Models each **worker** as a rich, structured profile: tagged niche skills,
   station/venue-type experience, verified work history, schedule availability,
   pay requirements, background signals.
2. Models each **role** as an equally rich requirement profile — not a job post,
   but a structured spec of what the restaurant actually needs.
3. Uses **AI reasoning** (not just keyword/attribute overlap) to argue *why* a
   given person fits a given role — connecting skills, history, schedule, pay,
   and culture the way a great GM's gut does, but explainably and at scale.

## Status

**Research phase.** Before building, we're doing deep research on the existing
landscape (Qwick, Instawork, Culinary Agents, Harri, Workstream, Indeed Flex,
AI-native entrants through mid-2026), the exact matching mechanics each uses,
their measured efficiency (fill rates, time-to-hire, retention), where they
fail for restaurants, and the 2025–26 state of the art in AI labor matching.

See [`research/`](research/) for the findings.

## Layout

- `research/` — market + matching-functionality research reports (cited)
