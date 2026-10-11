# Addendum: public records of Thunderstorm before Tinycast existed

Submitted by Droppy's developer (Jordy Spruit) as additional evidence for finding 6 and for the "Thunderstorm predates Tinycast" row in §7 of the report. It adds public, independently timestamped records; it does not change any other finding.

The Tinycast repository was created on **2026-06-29**. Each record below is earlier.

| Date and time (UTC) | Public record | What it says about Thunderstorm |
|---|---|---|
| 2026-03-20 (Discord share at 08:35) | Reddit, r/DroppyforMac: [Droppy v13.2.3 - Thunderstorm groundwork, recording HUD, scrolling …](https://www.reddit.com/r/DroppyforMac/comments/1ryqt2t/), shared in Droppy's Discord #updates as message `1484470550402170990` | Thunderstorm is named in the title of a public release post |
| 2026-04-19 19:41 | Droppy's Discord #updates, message `1495509658419593357` (Droppy 14.0.0 beta 1) | The public beta includes "a Spotlight-like replacement called 'Thunderstorm'", password-gated in that beta |
| 2026-06-14 18:27 | Droppy's Discord #updates, message `1515784643281158235` (Droppy 14.1.0 beta) | "Thunderstorm is now available for everyone, rebuilt as a Spotlight-style launcher with system actions (eject disks, uninstall apps, lock, sleep, restart, shut down)" |
| 2026-06-15 10:17 | Droppy's Discord #updates, message `1516023934573740143` (Droppy 14.1.0 beta 2) | "Thunderstorm: type 'quit all' or 'eject all' to close every app or eject every disk" |

Together with the Internet Archive snapshot of 2026-05-12 already cited in the report, this shows that before Tinycast existed, Thunderstorm was more than a name and an icon: a Spotlight-style launcher with system actions, available to every Droppy beta user from 14 June 2026.

## How to verify

The Discord server is public ([discord.gg/droppy](https://discord.gg/droppy)); each message opens at `https://discord.com/channels/1475948418986672158/1476247378205085879/<message id>`.

A Discord message ID is a snowflake that encodes the moment Discord created the message, so the dates above can be checked without trusting Droppy, and they cannot be edited after posting:

```bash
python3 -c "import datetime as d; [print(i, d.datetime.fromtimestamp(((i >> 22) + 1420070400000) / 1000, d.timezone.utc)) for i in (1484470550402170990, 1495509658419593357, 1515784643281158235, 1516023934573740143)]"
```

The Reddit post carries Reddit's own timestamp.

## Scope

This addendum is about when Thunderstorm existed and what it already did. Many of Thunderstorm's current features (the calculator, quicklinks, snippets, Raycast extensions, window layouts, backup) do first appear later, as the report says. The signed Droppy 13.1 installer (released 2026-03-16) has been offered to the author of this audit so its signing timestamp can be checked the same way as 15.2.2-beta.1.
