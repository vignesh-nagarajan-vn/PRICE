ABCSS 2026 guidelines and compliance check
Checked Nov 19, 2026. Updated Nov 20, 2026 against the acceptance email.

Paper ID S07214. Accepted Nov 2, 2026.

Workshop: The 11th International Workshop on Application of Big Data for
Computational Social Science (ABCSS2026), at IEEE BigData 2026.
Phoenix, Arizona, Dec 14-17, 2026, hybrid. The conference schedule puts
workshops on Dec 14.

The workshop page lists this paper among the 30 accepted (of 50 submitted),
with authors in the order Vignesh Nagarajan, Shriraghav Ashok.

Sources
- Workshop page: https://css-japan.com/abcss2026/
- Conference dates: https://bigdataieee.org/BigData2026/important-dates/
- Conference call for papers: https://bigdataieee.org/BigData2026/calls/papers/
- IEEE conference templates: https://www.ieee.org/conferences/publishing/templates.html


1. Dates

- Nov 26, 2026: camera-ready submission (workshop page, confirmed by the
  acceptance email)
- Nov 26, 2026: author registration deadline (workshop page and conference page)
- Dec 1, 2026: presentation videos due (conference page), 20 minutes maximum
- Dec 14, 2026: workshops

The acceptance email adds three things the public pages do not state. Camera-ready
uploads go to https://wi-lab.com/cyberchair/2026/bigdata26/index.php. Two extra
pages can be purchased at US$100 each, which this paper does not need at 8 pages.
The presentation slot is 25 minutes, 20 to talk and 5 for questions. A student
author registering alone pays the full rate, and a wire transfer takes about 10
days to clear.


2. What the workshop asks for

- Length: up to 10 pages. 6 to 8 pages are recommended.
- Format: IEEE Conference Proceedings format (the IEEE manuscript templates
  for conference proceedings).
- Review is single-blind, so author names stay on the paper.
- Papers that are registered and presented go to IEEE Xplore with the main
  conference papers.
- Questions: abcss [at] css-japan.com

The main conference call adds, for the same proceedings: IEEE 2-column format,
references count toward the page limit, no appendix.


3. Compliance check of the revised paper

Item                                  Rule                      Revised paper     Status
Page count                            10 max                    8                 OK
Recommended length                    6 to 8                    8                 OK (see note)
Template                              IEEE conference           IEEEtran          OK
                                                                [conference]
Layout                                2 columns, 10 pt          unchanged class   OK
                                                                defaults
Paper size                            US Letter                 8.5 x 11 in       OK
Margins                               template defaults         not altered       OK
References inside page count          yes                       yes               OK
Appendix                              not allowed               none              OK
Page numbers, headers, footers        none in IEEE conference   none              OK
Fonts embedded                        required for Xplore       all 32 embedded   OK
Type 3 fonts                          not accepted by Xplore    none              OK
Bookmarks and links                   none for Xplore           none              OK
Title and abstract free of math       IEEE template rule        yes               OK
Index terms present                   IEEE template             yes               OK
Author block                          names, affiliation,       as submitted      OK
                                      city, email
Figure captions below, table          IEEE style                yes               OK
captions above
Last page columns balanced            IEEE style                yes               OK

Note on length. The submitted version was 7 pages. With the revisions for the
three reviewers the paper came to 9 pages, and it was then cut to 8. Page 8 is
full: there is about one line of room left, so any added line pushes the
references onto a ninth page. The 9-page version is kept in the subfolder
"9-page version (before cuts)".

What was cut to reach 8 pages. No result, theorem, table or reference was
removed.
- Figures 1 to 3 now sit in one row across the top of page 4, at about 80% of
  their earlier size. Captions are unchanged.
- Abstract: the common-pool sentence and the pilot sentence are shorter.
- Section III-A: the modulus m_1 is defined in the line instead of on its own
  line.
- Section III-B, "Beyond dealers": dropped the sentence on two lenders scoring
  on the same features.
- Remark 1: dropped the clause comparing a monoculture with a fully diverse
  market.
- Section VII-A: the definition of "public data" is shorter.
- Section VII-D: dropped the sentence placing the estimate against the
  illustrative boundary s* = 0.37.
- Section IX: the pilot paragraph is shorter; its point about label errors
  moved into Section VII-D.

Note on the abstract. It is now about 275 words. The workshop sets no limit.
IEEE's general advice for Xplore is 150 to 250 words.


4. Things the public pages do not cover

The acceptance email does not carry the ISBN or the conference ID, so two items
are still open and the paper cannot be finalized without the first one.

The exact copyright line for the bottom of page 1 is the blocker. The paper still
has the placeholder 979-8-XXXX-XXXX-X/26/$31.00 (c)2026 IEEE from the submission,
at line 45 of source/main.tex, and it prints on page 1 of the PDF. The ISBN depends
on the proceedings, so it cannot be guessed. Ask the chairs for the exact string.

The IEEE PDF eXpress check needs the conference ID from the chairs. Run it after
the copyright line is in, and upload the file PDF eXpress returns. The IEEE
copyright form also has to be signed, through whatever link the chairs send.

Settled by the acceptance email: where to upload, and that at least one full
registration is due Nov 26.


5. Before submitting

- Both authors should read the abstract, Section VII-D and the new paragraph
  in the Conclusion. They report two pilot results that cut against the
  provenance story.
- Reviewer 2 asked for two things that are not closed. See the review reports
  beside this file. Page 8 is full, so adding either needs a matching cut.
  1. The firms' objective, with the definitions of epsilon, beta and gamma and
     the references they rest on.
  2. The equilibrium concept and information structure behind Theorem 4.


6. Changes made on Nov 20, 2026

Both are reductions, so neither can push the paper onto a ninth page. The PDF was
rebuilt from source afterwards and still comes to 8 pages, with 32 embedded fonts,
no Type 3 fonts, no overfull boxes and no undefined references.

Removed the claim that the pilot code is published. Section VII-D said "The code
and the correctness matrix are in [6]", pointing at the PRICE repository. The pilot
code and the MMLU correctness matrix are not there. A search of all 772 paths in
that repository returns nothing for pilot, MMLU, HELM or correctness. The sentence
is gone. The Table II numbers stay, and they now have no published code behind
them, which is the gap reviewer 3 pressed on. If the pilot folder is pushed before
Nov 26, restore the sentence.

Refreshed the access date on reference [6], from Sep. 19, 2026 to Nov. 20, 2026.

The separate claim that 542 numerical certificates pass, in Section I and
Section VII-A, does check out. ml-contributions/CERTIFICATES.md documents 542
assertions across eight verifier files, and the files are present.
