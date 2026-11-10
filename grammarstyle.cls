\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{grammarstyle}[2026/11/10 Contemporary Library reference grammar]
% All artwork is vector TeX; no external EPS conversion is required.
\newcommand{\DoNotLoadEpstopdf}{}
\LoadClass[10pt,twoside,openany]{book}

% ISO B5 (176 x 250 mm), with mirrored binding margins.
\RequirePackage[
    b5paper,
    inner=21mm,outer=17mm,top=20mm,bottom=19mm,
    headheight=12bp,headsep=14bp,footskip=24bp,
    marginparwidth=30bp,marginparsep=8bp
]{geometry}
\RequirePackage[table]{xcolor}
\RequirePackage{fontspec}
\RequirePackage[protrusion=true,expansion=true,stretch=15,shrink=15]{microtype}
\RequirePackage{amsmath}
\RequirePackage{unicode-math}
\RequirePackage{enumitem}
\RequirePackage{tabularx}
\RequirePackage{tabularray}
\RequirePackage{booktabs}
\RequirePackage{caption}
\RequirePackage[section]{placeins}
\RequirePackage{flafter}
\RequirePackage{needspace}
\RequirePackage{expex}
% Unicode math also names a relation \gla; preserve ExPex's language line.
\let\grammar@expexgla\gla
\RequirePackage{etoolbox}
\RequirePackage{multicol}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{tocloft}
\RequirePackage{tikz}
\RequirePackage{hyperref}
\RequirePackage{bookmark}

\definecolor{grammarIndigo}{HTML}{252D55}
\definecolor{grammarInk}{HTML}{20232A}
\definecolor{grammarTableHead}{HTML}{F1F2F0}
\definecolor{grammarRule}{HTML}{B5B8BC}
\definecolor{yaleblue}{rgb}{0.06,0.3,0.57}
\definecolor{darkgray}{HTML}{53606A}

\defaultfontfeatures{Ligatures=TeX,Renderer=HarfBuzz}
\setmainfont{Noto Sans}[
    BoldFont=Noto Sans Bold,
    ItalicFont=Noto Sans Italic,
    BoldItalicFont=Noto Sans Bold Italic,
    SmallCapsFeatures={Letters=SmallCaps}
]
\setsansfont{Noto Sans}[
    BoldFont=Noto Sans Bold,
    ItalicFont=Noto Sans Italic,
    BoldItalicFont=Noto Sans Bold Italic,
    SmallCapsFeatures={Letters=SmallCaps}
]
\setmathfont{FiraMath-Regular.otf}[Scale=MatchLowercase]
\newfontfamily\niklorskfont{Noto Sans SemiBold}[
    BoldFont=Noto Sans SemiBold,
    ItalicFont=Noto Sans SemiBold Italic,
    BoldItalicFont=Noto Sans SemiBold Italic
]

% Noto Sans punctuation has short sidebearings. Hang quotes and terminal
% punctuation optically, while keeping phonetic brackets and slashes aligned.
% Fontspec instance suffixes are ignored by microtype's family matching.
\SetProtrusion[name=grammar-noto,load=T1-default]
    {encoding=TU,family={NotoSans,NotoSansSemiBold}}
    {
        . = {,700}, {,} = {,550}, : = {,400}, ; = {,400},
        ! = {,200}, ? = {,150},
        ‘ = {650,650}, ’ = {650,650},
        “ = {550,550}, ” = {550,550},
        - = {400,400}, – = {300,300}, — = {200,200},
        / = {0,0}, [ = {0,0}, ] = {0,0}
    }
% Italic quotes already overhang their advance widths on the right.
\SetProtrusion[name=grammar-noto-italic,load=grammar-noto]
    {encoding=TU,family={NotoSans,NotoSansSemiBold},shape={it,sl}}
    {
        . = {,800}, {,} = {,650},
        ‘ = {850,200}, ’ = {850,200},
        “ = {700,300}, ” = {700,300}
    }

% Keep the chosen text size after lists, tables, and front matter.
\renewcommand\normalsize{%
    \@setfontsize\normalsize{10.4bp}{14.1bp}%
    \abovedisplayskip 8bp plus 2bp minus 3bp
    \abovedisplayshortskip 0bp plus 3bp
    \belowdisplayshortskip 5bp plus 3bp minus 3bp
    \belowdisplayskip \abovedisplayskip
    \let\@listi\@listI
}
\renewcommand\small{\@setfontsize\small{9.2bp}{12.2bp}}
\renewcommand\footnotesize{\@setfontsize\footnotesize{8.4bp}{11.2bp}}
\normalsize
\setlength{\parindent}{1.2em}
\setlength{\parskip}{0pt}
% Use the same word space after sentences, abbreviations, and vocabulary lemmas.
\frenchspacing
\setlength{\emergencystretch}{1.2em}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
\raggedbottom
\AtBeginDocument{\color{grammarInk}}

\hypersetup{
    unicode=true,colorlinks=true,
    linkcolor=grammarInk,citecolor=grammarInk,urlcolor=grammarIndigo,
    bookmarksnumbered=true,bookmarksopen=true,bookmarksopenlevel=0,
    pdftitle={A Grammar of Niklorsk},pdfauthor={Roel Christian Yambao},
    pdfdisplaydoctitle=true
}
\pdfstringdefDisableCommands{%
    \def\nk#1{#1}%
    \def\niklorsk#1{#1}%
    \def\ipa#1{#1}%
}

% Chapter-qualified labels support consultation across the whole grammar.
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{2}
\renewcommand{\thesection}{\thechapter.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}
\renewcommand{\thetable}{\thechapter.\arabic{table}}
\renewcommand{\thefigure}{\thechapter.\arabic{figure}}
\titleformat{\chapter}[display]
    {\normalfont\color{grammarInk}}
    {\fontsize{9bp}{12bp}\selectfont\color{grammarIndigo}\textls[80]{CHAPTER \thechapter}}
    {10bp}{\fontsize{29bp}{35bp}\selectfont\bfseries}
\titleformat{name=\chapter,numberless}[display]
    {\normalfont\color{grammarInk}}{}{0bp}
    {\fontsize{29bp}{35bp}\selectfont\bfseries}
\titlespacing*{\chapter}{0pt}{8bp}{26bp}
\titleformat{\section}
    {\normalfont\fontsize{14.3bp}{18bp}\selectfont\bfseries}
    {\thesection}{0.7em}{}
\titlespacing*{\section}{0pt}{19bp plus 3bp minus 2bp}{8bp}
\titleformat{\subsection}
    {\normalfont\fontsize{11.1bp}{14.1bp}\selectfont\bfseries}
    {\thesubsection}{0.7em}{}
\titlespacing*{\subsection}{0pt}{13bp plus 2bp minus 1bp}{6bp}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\fontsize{7.8bp}{10bp}\selectfont\thepage}
\fancyhead[RE]{\fontsize{7.8bp}{10bp}\selectfont\nouppercase{\leftmark}}
\fancyhead[LO]{\fontsize{7.8bp}{10bp}\selectfont\nouppercase{\rightmark}}
\fancyhead[RO]{\fontsize{7.8bp}{10bp}\selectfont\thepage}
\renewcommand{\headrulewidth}{0.35bp}
\renewcommand{\footrulewidth}{0pt}
\renewcommand{\chaptermark}[1]{\markboth{\thechapter\quad #1}{\thechapter\quad #1}}
\renewcommand{\sectionmark}[1]{\markright{\thesection\quad #1}}
\fancypagestyle{plain}{%
    \fancyhf{}%
    \fancyfoot[C]{\fontsize{9bp}{12bp}\selectfont\thepage}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0pt}%
}

% Contents and table lists remain black with a visible hierarchy.
\renewcommand{\cftchapfont}{\bfseries}
\renewcommand{\cftchappagefont}{\bfseries}
\renewcommand{\cftchapafterpnum}{\par\nobreak}
\renewcommand{\cftsecfont}{\normalfont}
\renewcommand{\cftsubsecfont}{\small}
\renewcommand{\cftsubsecpagefont}{\small}
\setlength{\cftbeforechapskip}{10bp}
\setlength{\cftbeforesecskip}{2bp}
\setlength{\cftbeforesubsecskip}{0bp}
\setlength{\cftchapnumwidth}{1.8em}
\setlength{\cftsecindent}{1.8em}
\setlength{\cftsecnumwidth}{2.6em}
\setlength{\cftsubsecindent}{4.4em}
\setlength{\cftsubsecnumwidth}{3.3em}
\setlength{\cfttabnumwidth}{3em}
\setlength{\cftbeforetoctitleskip}{8bp}
\setlength{\cftaftertoctitleskip}{26bp}
\setlength{\cftbeforelottitleskip}{8bp}
\setlength{\cftafterlottitleskip}{26bp}
\renewcommand{\cfttoctitlefont}{\fontsize{29bp}{35bp}\selectfont\bfseries}
\renewcommand{\cftlottitlefont}{\fontsize{29bp}{35bp}\selectfont\bfseries}

% Captions above paradigms, light rules, and quiet header shading.
\captionsetup[table]{position=top,skip=7bp,font=small,labelfont=normalfont,
    justification=raggedright,singlelinecheck=false,labelsep=space}
\AtBeginEnvironment{table}{\small}
\def\fps@table{!htbp}
\renewcommand{\tabularxcolumn}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\tabcolsep}{5bp}
\renewcommand{\arraystretch}{1.18}
\setlength{\heavyrulewidth}{0.6bp}
\setlength{\lightrulewidth}{0.35bp}
\SetTblrInner[tblr]{font=\small,
    row{1}={font=\bfseries,bg=grammarTableHead},
    hline{1,Z}={0.6bp,grammarInk},hline{2}={0.35bp,grammarInk},
    rowsep=3bp,colsep=5bp}
\setlength{\textfloatsep}{14bp plus 3bp minus 2bp}
\setlength{\intextsep}{12bp plus 2bp minus 2bp}
\setlength{\floatsep}{12bp plus 2bp minus 2bp}
\renewcommand{\topfraction}{0.92}
\renewcommand{\bottomfraction}{0.8}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.75}
\setcounter{topnumber}{3}
\setcounter{bottomnumber}{2}
\setcounter{totalnumber}{4}

% Preserve semantic manuscript commands; change their presentation only.
\newcommand{\yaleblue}[1]{\textcolor{yaleblue}{#1}}
\newcommand{\medium}[1]{{\niklorskfont #1}}
\newcommand{\niklorsk}[1]{\textcolor{yaleblue}{{\niklorskfont\upshape #1}}}
\newcommand{\nikp}[2]{\niklorsk{#1} `#2'}
\newcommand{\nikpp}[3]{\niklorsk{#1} [\ipa{#2}] `#3'}
\newcommand{\nk}[1]{\niklorsk{#1}}
\newcommand{\ipa}[1]{{\upshape #1}}
% Narrow vocabulary columns use natural word spaces, retaining entry indents.
\newcommand{\glossarypair}[3]{%
    \begingroup
    \edef\grammar@entryindent{\the\parindent}%
    \raggedright\setlength{\parindent}{\grammar@entryindent}%
    \nk{#1}. \textit{#2}, #3.\par
    \endgroup
}
% Compact dictionary entries begin at the column edge; wrapped lines hang.
\newcommand{\dictionarylabel}[1]{%
    {\normalfont\fontsize{7.8bp}{11.2bp}\selectfont\itshape #1}%
}
\newcommand{\dictionaryentry}[5]{%
    \par\begingroup
    \raggedright\setlength{\parindent}{0pt}%
    \setlength{\hangindent}{1.3em}\hangafter=1
    \setlength{\parskip}{1bp}%
    \noindent{\niklorskfont\upshape\color{grammarInk}#1%
        \ifstrempty{#2}{}{\textsuperscript{#2}}}%
    \nobreak\hspace{0.35em}\dictionarylabel{#3}%
    \ifstrempty{#4}{}{\space(\dictionarylabel{pl.}\ #4)}%
    % Definitions retain embedded forms as plain text; only the lemma is bold.
    \space{\let\nk\@firstofone\let\niklorsk\@firstofone #5}\par
    \endgroup
}
\newcommand{\vocabcentered}[1]{%
    \par\vspace*{5bp}\noindent\textbf{\MakeUppercase{#1}}\par\nobreak\vspace{3bp}%
}
\setlength{\columnsep}{18bp}
\setlength{\multicolsep}{12bp}

\gathertags
\lingset{exnotype=chapter.arabic,sampleexno=(7.99),
    everygla=\niklorskfont\upshape\color{yaleblue},
    everyglb=\normalfont\fontsize{9.2bp}{12bp}\selectfont,
    everyglft=\normalfont\fontsize{9.8bp}{13bp}\selectfont,
    aboveexskip=9bp,belowexskip=9bp,aboveglftskip=3bp,
    interpartskip=7bp,glspace=0.6em,splitpartspenalty=10000}
\pretocmd{\begingl}{\let\gla\grammar@expexgla}{}{}
\pretocmd{\chapter}{\excnt=1}{}{}
\setlist[enumerate]{topsep=7bp,itemsep=5bp,parsep=0pt}
\setlist[itemize,1]{leftmargin=2em,label={},topsep=5bp,itemsep=4bp,parsep=0pt,partopsep=0pt}

% Interior title page following the full-bleed cover.
\renewcommand{\maketitle}{%
    \begingroup
    \thispagestyle{empty}%
    \vspace*{53bp}%
    \noindent{\fontsize{25bp}{32bp}\selectfont\@title\par}%
    \vspace{17bp}%
    \noindent{\fontsize{12bp}{17bp}\selectfont\@author\par}%
    \vfill
    \noindent{\color{grammarRule}\rule{\textwidth}{0.5bp}}\par
    \endgroup
    \newpage
}
\input{preamble/cover}
