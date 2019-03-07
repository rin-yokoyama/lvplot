import sys
import yaml

from ROOT import TCanvas
from ROOT import TLine
from ROOT import TText
from ROOT import TGaxis
from ROOT import TArrow

if len(sys.argv) !=2 :
  print('usage: lvplot.py [yaml file]')
  sys.exit(1)
f = open(sys.argv[1],'r')
data = yaml.load(f)
f.close()

cv = data['Canvas']
canv = TCanvas(cv['name'],cv['title'],cv['xsize'],cv['ysize'])
plot_range = data['PlotRange']
canv.Range(plot_range['xmin'],plot_range['ymin'],plot_range['xmax'],plot_range['ymax'])

param = data['Parameters']

bands = data['Bands']
lines = []
texts = []
gamma = data['Gamma']
arrows = []
gtexts = []
dlines = []

for i, band in enumerate(bands):
  xmin = i*(param['width']+param['space'])
  xmax = xmin + param['width']
  xcenter = xmin + param['width']/2.
  levels = band['levels']
  texts.append(TText(xcenter,plot_range['ymin']+0.01*(plot_range['ymax']-plot_range['ymin'])+param['TextFloat'],band['name']))
  texts[-1].SetTextAlign(21)
  if 'color' in band:
    texts[-1].SetTextColor(band['color'])
  for level in levels:
    lines.append(TLine(xmin,level['energy'],xmax,level['energy']))
    texts.append(TText(xmin,level['energy']+param['TextFloat'],str(level['level'])))
    texts[-1].SetTextAlign(11)
    texts.append(TText(xmax,level['energy']+param['TextFloat'],str(level['energy'])))
    texts[-1].SetTextAlign(31)
    if 'noenergy' in band:
      texts[-1].SetText(0,0,'')
    if 'color' in band:
      texts[-1].SetTextColor(band['color'])
      texts[-2].SetTextColor(band['color'])
      lines[-1].SetLineColor(band['color'])
    if 'color' in level:
      texts[-1].SetTextColor(level['color'])
      texts[-2].SetTextColor(level['color'])
      lines[-1].SetLineColor(level['color'])
    if 'life' in level:
      texts.append(TText(xcenter,level['energy']+2*param['TextFloat']+(plot_range['ymax']-plot_range['ymin'])*param['TextSize'],str(level['life'])))
      texts[-1].SetTextAlign(21)
      texts[-1].SetTextColor(texts[-2].GetTextColor())

if 'Axis' in param:
  paxis = param['Axis']
  axis_margin = 0.015*(plot_range['ymax']-plot_range['ymin'])
  axis = TGaxis(-param['space'],paxis['range_min'],-param['space'],paxis['range_max'],paxis['range_min'],paxis['range_max'],paxis['ticks'],"")
  axis.SetTitle(paxis['title'])
  axis.SetLabelSize(paxis['label_size'])
  axis.SetTitleSize(paxis['title_size'])
  axis.SetTitleOffset(paxis['title_offset'])
  axis.Draw()
  
for line in lines:
  line.SetLineWidth(param['LineWidth'])
  line.Draw()

for text in texts:
  text.SetTextSize(param['TextSize'])
  text.Draw()

for i, g in enumerate(gamma):
  level1 = filter(lambda x: x.GetY1() == g['from'],lines)[0]
  level2 = filter(lambda x: x.GetY1() == g['to'],lines)[0]
  x1 = (level1.GetX1() + level1.GetX2())/2.0
  x2 = (level2.GetX1() + level2.GetX2())/2.0
  y1 = level1.GetY1()
  y2 = level2.GetY1()
  if level1.GetX1() < level2.GetX1():
    if level1.GetX2() - level2.GetX1() > param['space']:
      dlines.append(TLine(level1.GetX1(),y2,level2.GetX1(),y2))
      x2 = (level1.GetX1() + level1.GetX2())/2.0
    else:
      x1 = level1.GetX2()
      x2 = level2.GetX1()
  elif level1.GetX1() > level2.GetX1():
    if level1.GetX1() - level2.GetX2() > param['space']:
      dlines.append(TLine(level1.GetX2(),y2,level2.GetX2(),y2))
      x2 = (level1.GetX1() + level1.GetX2())/2.0
    else:
      x1 = level1.GetX1()
      x2 = level2.GetX2()
  if 'x1' in g:
      if g['x1'] == "center":
          x1 = (level1.GetX1() + level1.GetX2())/2.0
      elif g['x1'] == "left":
          x1 = level1.GetX1()
      elif g['x1'] == "right":
          x1 = level1.GetX2()
  if 'x2' in g:
      if g['x2'] == "center":
          x2 = (level2.GetX1() + level2.GetX2())/2.0
      elif g['x2'] == "left":
          x2 = level2.GetX1()
      elif g['x2'] == "right":
          x2 = level2.GetX2()
  if x1 == x2:
      for arrow in arrows:
          if x1 == arrow.GetX1() and x1 == arrow.GetX2() and not((y1 > arrow.GetY1() and y2 > arrow.GetY2()) or (y1 < arrow.GetY1() and y2 < arrow.GetY2())):
              x1 = x1 + 10
              x2 = x2 + 10

  arrows.append(TArrow(x1,y1,x2,y2))
  if 'energy' in g:
    gtexts.append(TText((x1+x2)/2.0+param['GTextOffset'], (level1.GetY1()+level2.GetY1())/2.0, str(g['energy'])))
  else:
    gtexts.append(TText((x1+x2)/2.0+param['GTextOffset'], (level1.GetY1()+level2.GetY1())/2.0, str(level1.GetY1()-level2.GetY1())))

for arrow in arrows:
  arrow.SetLineWidth(param['ArrowWidth'])
  arrow.SetArrowSize(param['ArrowSize'])
  arrow.SetAngle(param['ArrowAngle'])
  arrow.Draw(param['ArrowOption'])

for text in gtexts:
  text.SetTextSize(param['TextSize'])
  text.SetTextFont(12)
  text.Draw()

for line in dlines:
  line.SetLineWidth(param['LineWidth'])
  line.SetLineStyle(2)
  line.Draw()

canv.Print(data['OutputFile'])
