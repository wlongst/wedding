ceremony = ceremony.pdf
invitation = invitation.pdf
program = program.pdf

all: $(ceremony) $(invitation) $(program)
    
    
%.pdf: %.tex
	pdflatex $<

check: *.tex
	chktex $<
	ispell -t $<

clean:
	rm -f *.aux *.log *.out

spotless: clean
	rm -f *.dvi *.bak *.bbl *.blg *.pdf
