TARGET = paper
SRC = paper.tex \
      globaldefs.tex \
      introduction.tex \
      scenario.tex \
      testcases.tex \
      aft.tex \
      installation.tex \
      results.tex

BIB =
FIGS =
default: dvipdf

$(TARGET).dvi: $(SRC) $(BIB) $(FIGS)
	latex $(TARGET)
	-bibtex $(TARGET)
	latex $(TARGET)
	latex $(TARGET)

dvi: $(TARGET).dvi

pdf:
	pdflatex $(TARGET)
	bibtex $(TARGET)
	pdflatex $(TARGET)
	pdflatex $(TARGET)

dvipdf: $(TARGET).dvi
	dvipdf $(TARGET)
	cp $(TARGET).pdf ../usermanual.pdf

pspdf: $(TARGET).dvi
	dvips $(TARGET)
	ps2pdf $(TARGET).ps

clean:
	rm -rf *.log $(TARGET).dvi $(TARGET).pdf $(TARGET).ps *.aux $(TARGET).bbl $(TARGET).blg $(TARGET).toc $(TARGET).out $(TARGET).lof $(TARGET).lot
