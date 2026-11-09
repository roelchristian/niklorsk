\ProvidesClass{grammarstyle}[2024/04/10 Niklorsk Grammar Class]
\LoadClass{amsbook}

% ---- Basic Package and Layout Configuration ----
\RequirePackage[paperwidth=6in, paperheight=9in]{geometry}
\geometry{
    verbose,
    tmargin=1.1in,
    bmargin=1.1in,
    lmargin=0.7in,
    rmargin=0.7in,
    marginparwidth=0.5in,
    marginparsep=0.1in,
}

\widowpenalty10000
\clubpenalty10000

\RequirePackage{xcolor}
\RequirePackage{hyperref}
\RequirePackage{enumitem}
\RequirePackage{tabularx}
\RequirePackage{tabularray}
\RequirePackage[tableposition=top]{caption}
\RequirePackage{fontspec}
\RequirePackage{expex}
\RequirePackage{etoolbox}
\RequirePackage{multicol}
\RequirePackage{microtype}

% Fonts and Typography
\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Noto Sans}
[
    BoldFont=Noto Sans SemiBold,
    ItalicFont=Noto Sans Italic,
    BoldItalicFont=Noto Sans SemiBold Italic,
    Scale=0.9
]

% ---- Document-Wide Style Adjustments ----
\setlist[itemize,1]{label=--}

\hypersetup{
    colorlinks,
    linkcolor=darkgray,
    citecolor=darkgray,
    urlcolor=darkgray
}

\captionsetup[table]{skip=10pt, font={small}}

% Color Definitions
\definecolor{yaleblue}{rgb}{0.06, 0.3, 0.57}
\definecolor{darkgray}{rgb}{0.45, 0.45, 0.45}

% ---- Niklorsk-specific Commands and Styling ----

% ---- Styling for Niklorsk Text ----
\newcommand{\yaleblue}[1]{\textcolor{yaleblue}{#1}} 
\newcommand{\medium}[1]{{\bfseries #1}}

\newcommand{\niklorsk}[1]{\yaleblue{\medium{#1}}} % Niklorsk text
\newcommand{\nikp}[2]{\niklorsk{#1} `#2'}
\newcommand{\nikpp}[3]{\niklorsk{#1} [\ipa{#2}] `#3'}
\newcommand{\nk}[1]{\niklorsk{#1}}

% Redefine /scshape and /textsc to use Noto Sans
\renewcommand{\scshape}{\fontspec{Noto Sans}[Letters=UppercaseSmallCaps]}
\renewcommand{\textsc}[1]{\scshape{#1}}


% ---- Styling for IPA Text ----
% \newfontfamily\ipafont{Noto Sans}[Scale=0.9]
\newcommand{\ipa}[1]{{#1}}

% ---- Styling for Glossary Items ----
\newcommand{\glossarypair}[3]{\nk{#1}. \textit{#2}, #3.}
\newcommand{\vocabcentered}[1]{{\small \begin{center} \textbf{#1} \end{center}}}

\gathertags
\lingset{
    everygla=\bf\color{yaleblue},
    everyglb=\footnotesize,
    everyglft=\footnotesize,
    aboveexskip=5pt,
    aboveglftskip=0pt,
    belowexskip=5pt
}

% Reset example counter at the beginning of each chapter
\pretocmd{\chapter}{\excnt=1}{}{}

% Triple default itemize left margin, remove bullet points, add one empty line before and after each item
\setlist[itemize,1]{left=3em, label={}, topsep=5pt, parsep=0pt, partopsep=0pt}

\raggedbottom
