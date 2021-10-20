\NeedsTeXFormat{LaTeX2e}

\ProvidesClass{invoice}
\LoadClass[10pt]{letter}

\RequirePackage[utf8]{inputenc}
\RequirePackage[colorlinks]{hyperref}
\RequirePackage[left=1in,top=1in,right=1in,bottom=1in]{geometry} % Document margins
\RequirePackage{graphicx}
\RequirePackage{tabularx}
\RequirePackage{multirow}
\RequirePackage{ragged2e}
\RequirePackage{hhline}
\RequirePackage{array}
\RequirePackage{xcolor}


\hypersetup{
    urlcolor=blue
}

\newcolumntype{R}[1]{>{\raggedleft\let\newline\\\arraybackslash\hspace{0pt}}m{#1}}
