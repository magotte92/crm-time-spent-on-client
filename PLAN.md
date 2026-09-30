# Plan: make the office time log actually usable

This is a direction for a later implementer. It does not change application code. Versions below were checked against PyPI and the Django download page on 30 September 2026.

The dependency bump in `10aa656` (Django 5.2.17, Python 3.12) is already on `master`. Do not repeat it. The product behavior underneath that bump is still the 2019 app.

## 1. Idea

A small internal web app for a Greek accounting office. Staff sign in, pick a client, a task and a subtask, and a duration bucket (5 minutes up to 8 hours), and that row is stored against their username. A second, staff-only area is meant to answer: how much time did we spend on each client, on each kind of work, and per person per day.

Evidence, and where it is thin:

- README: "A simple crm web app to record the time employees spent on clients."
- UI copy is Greek (`Καταγραφή χρόνου`, `Επωνυμία`, `Κατηγορία`). `LANGUAGE_CODE` is `el`, `TIME_ZONE` is `Europe/Athens`.
- The login footer credits Gkatziaris Pantelis, 2019. The favicon path is a ROMVOS mark. Treat "ROMVOS" as a brand asset in the repo, not as a confirmed legal entity.
- Committed CSV extracts use categories such as phone support, accounting/tax, and payroll. That is why this reads as an accounting practice's client-time log, not a sales CRM. There is no pipeline, invoice, or contact record in the models.
- Uncertainty: nothing in git says whether the live office still uses this, or whether "Anton" (the `/anton/` URL prefix and missing `anton.html`) was one specific manager's dashboard. Keep that prefix until someone who uses it says otherwise.

What it is not: a general CRM, a billing system, or an employee punch clock. Do not grow it into one.

## 2. Current stack

How it runs today:

- Python 3.12, Django 5.2.17 (`requirements.txt` and `Pipfile`). CI (`.github/workflows/ci.yml`) installs `requirements.txt` and runs `python manage.py test` on Ubuntu.
- SQLite file `db.sqlite3` (gitignored). `server transfer.txt` is a note for a later dump/load onto MySQL or PostgreSQL. Nothing in settings implements that.
- `python manage.py runserver`, plus `start_site.bat`, which `cd`s to a hardcoded `E:\git-projects\...` path and binds `0.0.0.0:8000`. `notify.bat` is a Windows `msg` popup telling people to log their hours. It is not part of the Django process.
- Server-rendered Django templates. Bootstrap 4.3.1 and jQuery 3.3.1 are loaded from CDNs (StackPath and code.jquery.com). django-autocomplete-light 5.0.0 (`dal` / `dal_select2`) drives the client picker.
- Reports in `employee/views.py` pull rows into pandas 3.0.6, write `stuff/*.csv`, read that CSV back, and group it. NumPy 2.5.3 comes along for pandas.
- Django REST framework 3.18.1 is installed. `core/serializer.py` defines `TestSerializer` and nothing routes to it.
- `python-dotenv` is installed and unused. `SECRET_KEY` is a string literal in `app/settings.py`. `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, `USE_TZ = False`.
- Auth is `django.contrib.auth`. Login redirects to `/recorder/`. Logout on the entry form is POST, which matches Django 5, and `core/tests.py` covers that.
- Apps: `core` (models and the entry form), `employee` (reports, no models), `csv_upload_app` (one client CSV upload view, no models), `panel` (a report view that is not in `INSTALLED_APPS` and not included from `app/urls.py`).

Domain model (`core/models.py`):

| Model | Role |
| --- | --- |
| `Clientele` | Client name. Primary key column is `Aa`. |
| `Task` / `SubTask` | Work category and reason. Subtask points at its parent task. |
| `ClientModel` | One time entry: client, task, subtask, `time_spent` as a `CharField` of minute counts (`"5"`, `"30"`, `"90"`), `dec_name` as a `CharField` set to `str(request.user)`, `date_added` with `auto_now=True`. |

`core/tests.py` covers system check, login, creating one entry, autocomplete, logout, and the pandas aggregations by calling `get_context_data()` directly. It does not render the report templates.

Known breaks a later implementer will hit immediately:

- `templates/anton.html`, `templates/timer.html`, and `templates/all_employees.html` do not exist. `all_clients.html`, `all_tasks.html`, `employee_tab.html`, and `clientsum.html` all `{% extends "anton.html" %}`. Hitting those URLs raises `TemplateDoesNotExist`. The tests never notice.
- `employee/urls.py` wraps every report in `permission_required('is_staff')`. `is_staff` is a user flag, not a permission codename, so the decorator does not mean "staff only".
- `AntonPage` and `TimeBasedPage` build a today-filtered queryset named `data` and then put the unfiltered `qs` into the template context.
- `employee_tab.html` unpacks `(name, time_spent, date_added)` but the frame columns are `(dec_name, date_added, time_spent)`, so the date and duration columns are swapped on screen.
- `make_all_employees()` selects three values and builds a four-column frame. Its URL is commented out.
- `date_added` uses `auto_now`, so any later `save()` rewrites the business date.
- Every report GET rewrites `stuff/all.csv` or `stuff/employees.csv`. Two people opening a report at once clobber the same files. The test suite copies that directory aside and copies it back.
- `static/javascript/manage_records.js` is referenced and missing. The favicon is `static/graphics/ROMVOS.png`; the repo only has `romvos_ICO.svg`.
- Client search uses `name__istartswith=self.q.upper()`, so a lowercase query only matches names that were stored in uppercase.
- Entry-form labels are translated by walking the DOM in `manage_records.html` (`Name:` → `Επωνυμία:`).
- `panel` writes `./media/recent.csv` on GET and is unwired.
- Two historical `0005_*` migrations both descended from `0004_example`. `0008_merge_example_branch` merges them, and `0005_delete_example` was turned into a no-op so a fresh database can migrate. Leave that history alone.
- `requirements.txt` and `Pipfile` both pin the same stack. CI trusts only the requirements file.

## 3. Modern fit

Stay a server-rendered Django app. The office flow is one form and a handful of tables. A SPA, Odoo, or a hosted time tracker would be a different product.

Prefer the LTS already in the repo over the current feature release. As of 30 September 2026 the supported Django lines are 5.2 LTS (5.2.17, security fixes through April 2028), 6.0 (extended support through April 2027), and 6.1.1 (mainstream through April 2027, extended through December 2027). Django 6.1 is real and maintained. It is the wrong default here: this app just moved to 5.2, and 5.2 is supported longer.

| Candidate | Use it? | Why |
| --- | --- | --- |
| Django 5.2.17, Python 3.12 | Default, already installed | Security support into 2028. CI already runs this pair. Python 3.12's own security support runs to October 2028. |
| Django 6.1 | Not now | Shorter support than 5.2, and it would be a second upgrade before the reports even render. Revisit when 6.2 LTS exists (April 2027 on the current schedule) or when 5.2 extended support is close to ending. |
| django-autocomplete-light 5.0.0 | Keep for now | Already pinned. 5.1.0rc2 (9 September 2026) is a release candidate; do not chase it. The 5.0 line still speaks Select2, which matches `autocomplete.ModelSelect2` in `core/forms.py`. |
| django-htmx 1.29.0 (htmx 2, the library default) | Phase 3, if the Select2 widget keeps hurting | Adam Johnson's package, Django 5.2–6.1, htmx 2 by default. htmx 4 is still beta inside 1.29.0 (`version=4`). Do not opt into the beta. |
| django-filter 26.1 | Yes, for the date-range reports | CalVer, requires Django ≥ 5.2. Replaces the unused daterangepicker script in `static/javascript/all_clients.js`. |
| django-import-export 4.4.1 | Yes, for client CSV | Admin import with a preview step, semicolon CSV via tablib, permission checks. Replaces the hand-rolled `/magotte/csv_upload_app/` view. |
| pandas 3.0.6 / numpy 2.5.3 | Remove from the web process | Fine libraries, wrong job. Aggregations of a few thousand office rows belong in SQL. The CSV round-trip is the bug. |
| djangorestframework 3.18.1 | Remove unless a caller appears | No view uses it. Keeping it adds a dependency and an unused serializer. |
| django-environ 0.14.0 | Yes | `python-dotenv` is already installed and settings ignore it. django-environ reads `DATABASE_URL` and casts `DEBUG`. |
| WhiteNoise 6.12.0 | Yes, when serving for real | Serves collected static files from the WSGI app. No separate nginx required on the office PC. |
| waitress 3.0.2 | Yes, for the Windows box this repo targets | `start_site.bat` is Windows. gunicorn does not run natively there. Waitress is a maintained WSGI server. Use gunicorn only if this moves to Linux. |
| PostgreSQL 16 or 17 + psycopg 3.3 | Only if one SQLite file becomes the bottleneck | Django 5.2 supports PostgreSQL 14+. SQLite is the right default for a single office process. `server transfer.txt` already sketches a dump/load. |
| pytest-django 4.14.0 and ruff 0.16.9 | Optional in phase 3 | `manage.py test` is enough and already in CI. Switch only if the suite grows past what `TestCase` wants. Do not block phases 1–2 on a test-runner migration. |
| Bootstrap 5.3 (vendored under `static/`) | Yes | The StackPath Bootstrap 4.3.1 URL is a dead hosting pattern. Vendor the CSS so the office PC works without that CDN. |
| django-allauth, Celery, Channels, a React front end | No | No social login, no background jobs, no live updates in this product. |

## 4. Proposed direction

One Django project, two jobs: record a time entry, and read aggregates. SQLite stays the default database. Settings grow a `DATABASE_URL` escape hatch and nothing else.

Defaults:

- Runtime: Python 3.12, Django 5.2.x (stay inside `>=5.2.17,<5.3` until a deliberate upgrade).
- Entry form: keep `PushTask`, the grouped subtask field in `core/fields.py`, and DAL 5.0 Select2 until phase 3.
- Reports: one queryset module that uses `Sum`, `Avg`, `Min`, `Max` on an integer minute column. Templates render those rows. No CSV in the request path.
- Staff gate: `staff_member_required` (or `UserPassesTestMixin` checking `is_staff`). Ordinary logged-in users can record time. Only staff open `/anton/`.
- Dates: `worked_on` is a `DateField` the user can set (default today, Europe/Athens). `created_at` is `auto_now_add`. Stop using `auto_now` as the business date. Leave `USE_TZ` False until `worked_on` is a date, so the office does not pick up a UTC shift by accident. Turn time zones on only after that field exists and the tests cover "today" in Athens.
- Employee: `ForeignKey` to `User`, populated from the current `dec_name` strings. Keep `dec_name` for one release as a read-only copy if a dump still needs it, then drop it.
- Minutes: `PositiveSmallIntegerField` with the existing choices. Migrate by casting the current numeric strings.
- Client import and full export: django-import-export on `Clientele` and `ClientModel` in the admin, plus one streaming CSV download for the staff export. Delete `csv_upload_app` and the unwired `panel` app once their behavior lives in admin and in the ORM reports.
- Secrets: `django-environ`. No secret in the repo. Rotate the key that is already committed; anyone with the git history has it.
- Deploy: `waitress` serving `app.wsgi:application`, WhiteNoise, `DEBUG=False`, an explicit `ALLOWED_HOSTS`. Document that in the README when it is implemented. `runserver` stays the development command.
- Package file: `requirements.txt` is the source of truth because CI installs it. Delete `Pipfile` / `Pipfile.lock` in the same change that next touches dependencies, so they cannot drift again.
- Primary key column `Aa`: leave it. Renaming the column touches every row and buys nothing the office can see.

Alternatives, if a default hurts:

- If DAL 5.0's Select2 assets break under a later 5.2 patch, replace the client widget with an htmx 2 search box (`django-htmx` 1.29, default htmx 2). Do not upgrade to a DAL release candidate to get there.
- If the office outgrows one SQLite writer, set `DATABASE_URL` to PostgreSQL and install `psycopg[binary]`. Do not introduce MySQL unless they already have a server; the transfer note lists both, and PostgreSQL is the one Django's own docs prefer.
- If a phone client appears later, add a small JSON view then. DRF is justified at that point. It is not justified by `TestSerializer`.

Target shape after phase 2:

```
app/settings.py          env-driven DEBUG, hosts, SECRET_KEY, DATABASE_URL
core/models.py           Clientele, Task, SubTask, ClientModel (minutes, user, worked_on)
core/views.py            recorder + autocomplete
core/reports.py          ORM aggregates
employee/views.py        thin template views over core.reports
templates/anton.html     staff shell: nav, date filter, {% block content %}
```

`employee` can keep its name. Renaming the app label is a migration for no user-visible gain.

## 5. Phased implementation

Each step names the check that should go in `core/tests.py` (or a new `employee/tests.py`) and pass under `python manage.py test` before the next step starts. Do not weaken the existing smoke tests.

### Phase 1 — pages render, access matches the words on the screen

1. Add `templates/anton.html`: a staff layout with links to the existing report names (`all_clients`, `employees`, `client_sum`, `all_tasks`) and `{% block content %}`. Point the favicon at `graphics/romvos_ICO.svg`, or add the missing PNG. Drop the script tag for the missing `manage_records.js`, or add an empty file only if something else needs it.
   - Test: a staff user `GET`s `reverse('all_clients')`, `employees`, `client_sum`, and `all_tasks` and gets 200. The response body contains the fixture client name.
2. Replace `permission_required('is_staff')` with `staff_member_required`. Do this in the same change as step 1, or the new template test will describe the wrong audience.
   - Test: a normal user gets 302 to login (or 403) on `all_clients`. A user with `is_staff=True` gets 200.
3. Fix `employee_tab.html` so the columns follow the frame: person, date, duration.
   - Test: render `EmployeeTabPageView` with the test client and assert the HTML order, not only `get_context_data()`.
4. Delete `AllEmployeesPage`, `make_all_employees`, `AntonPage`'s discarded filter, and `TimeBasedPage`, or make them real. Recommended: delete the commented `all_employees` route and the two views whose templates do not exist, until phase 2 adds a date filter on the pages that do exist. `ExportAllPageView` can stay if its test renders `base.html` and asserts the CSV appears — but prefer deleting the disk write in phase 2 rather than polishing it.
   - Test: `django.urls.reverse` no longer resolves the removed names, and `manage.py check` is clean.
5. Autocomplete: filter with `name__icontains`, still scoped to authenticated users.
   - Test: query `ac` and `AC` both return `ACME`. An anonymous GET returns an empty result.
6. Stop the test `setUp` from copying `stuff/` out and back. Reports should write under a temp directory the test controls (`override_settings` or a monkeypatched path). Production extracts must not be a test fixture.
   - Test: the suite passes with `stuff/` absent.
7. Move `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` to environment variables via django-environ. Development default for `DEBUG` may be true when the env var is missing; the committed file must not contain a usable production secret. Rotate the key that is in git history. Add `stuff/*.csv` and `media/` to `.gitignore` (the files already tracked stay in history; see risks).
   - Test: with `SECRET_KEY` set in the environment, `manage.py check` passes. A unit test of the settings helper rejects an empty key when `DEBUG` is false.

Phase 1 is done when a staff user can open every linked report in a browser and a non-staff user cannot, and CI is green without the committed CSVs.

### Phase 2 — the numbers come from the database

8. Add `minutes` as a `PositiveSmallIntegerField`. Data-migrate `time_spent` by casting the digit strings. Keep accepting the same choice values in the form. Remove the `CharField` once the tests read `minutes`.
   - Test: a row stored as `"90"` becomes `90`, and `90 + 30` sums to `120` in the database, not by reading a CSV.
9. Add `employee` as a `ForeignKey` to `User` (`PROTECT`). Data-migrate by matching `dec_name` to `username`. Rows with no matching user fail the migration loudly (print the distinct unmatched names and stop) rather than being attached to a guessed account.
   - Test: posting the recorder form sets `employee` to the logged-in user.
10. Add `worked_on = DateField(default=date.today)` and `created_at = DateTimeField(auto_now_add=True)`. Copy the date part of `date_added` into `worked_on`, then stop updating `date_added` (remove `auto_now`). Show `worked_on` on the entry form so someone can log yesterday.
    - Test: saving an existing row does not change `worked_on` or `created_at`. A new row defaults `worked_on` to today.
11. Rewrite `AllClientsPageView`, `SumOfClientView`, `AllTaskPage`, and `EmployeeTabPageView` to call ORM aggregates. Delete `make_all_client` and `make_all_employee`. The views must not create files.
    - Test: the same totals as `test_report_views_aggregate_minutes`, and `stuff/all.csv` is not created during the request.
12. Add a `worked_on` from/to filter with django-filter on the staff pages. Default the range to the current month so the page is not an unbounded dump.
    - Test: a row dated yesterday is excluded when the range is today, and included when the range covers yesterday.
13. Replace `csv_upload_app` with an admin import of `Clientele` (semicolon-separated, columns matching the current `Aa` and name behavior, preview before commit). Unknown columns fail validation. Remove the `/magotte/csv_upload_app/` route and the `admin.can_add_log_entry` permission check.
    - Test: a two-line CSV creates clients; a `.txt` upload is rejected; a non-staff user cannot import.
14. Replace `ExportAllPageView`'s disk write with an authenticated staff `StreamingHttpResponse` (or django-import-export's export) of client, task, subtask, minutes, employee, `worked_on`.
    - Test: status 200, `Content-Disposition` attachment, header row present, body contains the fixture client, no file left in `stuff/`.
15. Remove `rest_framework` from `INSTALLED_APPS`, delete `core/serializer.py`, and drop `djangorestframework` from `requirements.txt` if step 14 did not need it.
    - Test: `manage.py check` and the full suite pass with the package uninstalled.

Phase 2 is done when the report tests pass on a machine whose `stuff/` directory does not exist.

### Phase 3 — polish the office PC

16. Vendor Bootstrap 5.3 CSS under `static/vendor/` and drop the StackPath, jQuery slim, and Popper CDN tags on the entry and login pages. Keep DAL's own assets. Set Greek `labels` on `PushTask` and delete the DOM label rewriter.
    - Test: recorder HTML contains `Επωνυμία` and does not contain `stackpath.bootstrapcdn.com`.
17. If the Select2 client field is still awkward after step 16, swap it for an htmx 2 combobox (django-htmx 1.29, no `version=4`). The search view stays the authenticated `ClientAutocomplete` queryset.
    - Test: a request with `HX-Request: true` returns a fragment containing the match and does not return the full recorder page.
18. Serve the app with waitress and WhiteNoise. Replace `start_site.bat`'s `runserver` line with waitress bound to the office PC's LAN address, not `0.0.0.0` unless they mean that. Add a one-page run section to the README: migrate, collectstatic, waitress, create a staff user.
    - Test: `manage.py collectstatic --dry-run` succeeds. A smoke test imports `app.wsgi:application`.
19. Drop pandas, numpy, six, and pytz from direct requirements once no import remains. Keep `python-dateutil` only if something still imports it (Django and pandas were the consumers).
    - Test: `python -c "import employee.views"` works in a venv installed from the trimmed requirements, and `manage.py test` passes.
20. Add ruff to CI only after the above is green. Fix what it flags in the files already being edited; do not reformat the whole history in one drive-by.

## 6. Out of scope / risks

- Do not build invoicing, payroll calculation, client portals, or a mobile app. The categories in the old extracts describe work types; they are not a spec for an accounting engine.
- Do not add employee surveillance: no keystroke logging, no always-on timers that start without a person submitting the form, no hidden screenshots. `notify.bat` is a manual Windows reminder. Leave it or delete it; do not replace it with something that watches people.
- Secrets: the Django secret in `app/settings.py` is in git history. Moving it to the environment does not un-leak it. Rotate it. Do not print the old value in issues or in this file.
- Personal data: `stuff/all.csv`, `stuff/employees.csv`, and `stuff/all_employees.csv` are tracked and contain real client names and staff email addresses. That is office data, likely personal data under GDPR, sitting in a public-style git history (the repo is world-readable if GitHub is). Stop using those files as runtime storage (phase 2). Add them to `.gitignore` for new dumps. Deleting them from history needs the repo owner: it is a history rewrite and a force-push, which this plan does not authorize. Until that happens, do not copy the CSVs into new fixtures, docs, or tests.
- The CSV upload accepts an `Aa` primary key from the file and `update_or_create`s it. A bad file can overwrite clients. The admin importer in phase 2 must preview and must not trust a primary key from an unreviewed file unless the operator confirms an update.
- `permission_required('is_staff')` and the missing templates mean the staff area is already broken. Fixing the permission will make those URLs reachable by staff for the first time. Confirm with the office before exposing historical rows to every `is_staff` account.
- `USE_TZ = False` plus `Europe/Athens` is consistent only while business dates are dates, not UTC datetimes. Do not flip `USE_TZ` in the same change as the Django pin.
- `start_site.bat` binds every interface with the development server and `DEBUG` on. That is the production risk, not the choice of database.
- Dead integrations: grappelli is commented out; DRF has no clients; StackPath Bootstrap can 404; `manage_records.js` 404s. None of these are external APIs with terms of service to migrate. There is no payment, map, or government API in the code.
- Hardware: a single Windows PC is the deployment this repo describes. No GPU, no queue, no container requirement. Waitress on that PC is enough.
- Legal: the code is MIT, copyright humble-goat, 2019. The client extracts are not covered by that license. Do not publish them as sample data.
- Migration landmine: do not regenerate or renumber `core/migrations/0001` through `0008`. Add `0009` onward. A fresh database must keep migrating through the merge.

## 7. Success criteria

The improvement worked when all of the following are true on a clean checkout, Python 3.12, packages from `requirements.txt`:

- `python manage.py check` and `python manage.py test` pass with no `stuff/*.csv` present.
- A logged-in non-staff user can open `/recorder/`, submit client + subtask + duration, and sees that entry stored as integer minutes on their user.
- A staff user can open the client, employee, client-total, and task reports and see those minutes summed. A non-staff user cannot open them.
- Those report views do not create or modify files under `stuff/` or `media/`.
- Filtering the report to a single day hides entries outside that day.
- Importing a semicolon client CSV is previewed in admin and does not require the `/magotte/` route.
- Export returns a CSV download to staff and writes nothing to disk.
- `app/settings.py` contains no live secret. `DEBUG` and `ALLOWED_HOSTS` come from the environment on the office PC, and the PC is served by waitress rather than `runserver`.
- The entry form shows Greek field labels without a JavaScript text replace.
- Direct dependencies no longer include pandas, numpy, or djangorestframework.
- The recorder and the four staff reports still do the same job the README describes: record time employees spent on clients, and show the totals.
