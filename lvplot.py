import sys
import yaml
import array
import ROOT
from ROOT import TCanvas
from ROOT import TLine
from ROOT import TText
from ROOT import TGaxis
from ROOT import TArrow
from ROOT import TBox

def FixSpacing(txts,space):
  count = 0
  for text1 in txts:
    for text2 in txts:
      if text1.GetX() == text2.GetX():
        diff = text1.GetY()-text2.GetY()
        if diff < space and diff > 0:
          text1.SetY(text2.GetY()+space)
          count = count + 1
  
  return count
    
if __name__ == '__main__':
  ROOT.gROOT.SetBatch()

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
  pages = data['Pages']

  canv.Print(data['OutputFile']+'[')
  for i, page in enumerate(pages):
    daughters = page['Daughters']
    ttexts = []
    alllines = []
    texts = []
    arrows = []
    gtexts = []
    dlines = []
    boxes = []
    xmin = 0

    for d_i, daughter in enumerate(daughters):
      lines = []
      levels = daughter['Levels']
      gamma = daughter['Gamma']
      ngamma = len(gamma)
      x_width = 2.0*param['TextOffset']+2.0*param['TextSpace']+(ngamma+1)*param['width']
      ttexts.append(TText(xmin+(ngamma+1)*param['width']/2.0,param['TitleTextOffset'],str(daughter['Name'])))

      lstyles = {}
      lcolors = {}
      for level in levels:
        xmax = xmin + (ngamma+1)*param['width']
        lines.append(TLine(xmin,level['energy'],xmax,level['energy']))
        texts.append(TText(xmin-param['TextOffset'],level['energy']+param['TextFloat'],str(level['level'])))
        texts[-1].SetTextAlign(31)
        texts.append(TText(xmax+param['TextOffset'],level['energy']+param['TextFloat'],str(level['energy'])))
        texts[-1].SetTextAlign(11)
        lstyles.update({texts[-1]:1})
        lstyles.update({texts[-2]:1})
        lcolors.update({texts[-1]:1})
        lcolors.update({texts[-2]:1})
        if 'color' in level:
          texts[-1].SetTextColor(level['color'])
          texts[-2].SetTextColor(level['color'])
          lines[-1].SetLineColor(level['color'])
          lcolors.update({texts[-1]:level['color']})
          lcolors.update({texts[-2]:level['color']})
        if 'style' in level:
          lines[-1].SetLineStyle(level['style'])
          lstyles.update({texts[-1]:level['style']})
          lstyles.update({texts[-2]:level['style']})

      while(FixSpacing(texts,param['TextSpace'])):
        print 'fixing spacing'

      for text in texts:
        xmax = xmin+(ngamma+1)*param['width']
        if text.GetX() == xmax+param['TextOffset']:
          lines.append(TLine(xmin-param['TextWidth'],text.GetY()-param['TextFloat'],xmin-param['TextOffset'],text.GetY()-param['TextFloat']))
          lines.append(TLine(xmax+param['TextWidth'],text.GetY()-param['TextFloat'],xmax+param['TextOffset'],text.GetY()-param['TextFloat']))
          lines.append(TLine(xmin-param['TextOffset'],text.GetY()-param['TextFloat'],xmin,float(text.GetTitle())))
          lines.append(TLine(xmax+param['TextOffset'],text.GetY()-param['TextFloat'],xmax,float(text.GetTitle())))
          style = lstyles[text]
          color = lcolors[text]
          for txtid in range(1,5):
            lines[-txtid].SetLineStyle(style)
            lines[-txtid].SetLineColor(color)

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
        alllines.append(line)

      for text in texts:
        text.SetTextSize(param['TextSize'])
        text.Draw()

      for i_g, g in enumerate(gamma):
        level1 = filter(lambda x: x.GetY1() == g['from'],lines)[0]
        level2 = filter(lambda x: x.GetY1() == g['to'],lines)[0]
        x1 = xmin + (i_g+1)*param['width']
        x2 = xmin + (i_g+1)*param['width']
        y1 = level1.GetY1()
        y2 = level2.GetY1()

        arrows.append(TArrow(x1,y1,x2,y2))
        txt = ""
        txtx = (x1+x2)/2.0
        txty = y1+param['TextOffset']
        if 'energy' in g:
          txt = str(g['energy'])
        else:
          txt = str(level1.GetY1()-level2.GetY1())
        gtexts.append(TText(txtx, txty, txt))
        gtexts[-1].SetTextAlign(12)
        gtexts[-1].SetTextAngle(90)
        gtexts[-1].SetTextSize(param['TextSize'])
        gtexts[-1].SetTextFont(12)
        gtexts[-1].Draw()
        wbox_px = array.array('I',[0])
        hbox_px = array.array('I',[0])
        gtexts[-1].GetTextExtent(wbox_px,hbox_px,txt)
        xscale = abs(canv.PixeltoX(1)-canv.PixeltoX(0))
        yscale = abs(canv.PixeltoY(1)-canv.PixeltoY(0))
        wbox = xscale*float(hbox_px[0])
        hbox = yscale*float(wbox_px[0])
        boxes.append(TBox(x1-wbox/2.0,y1+param['TextOffset'],x1+wbox/2.0,y1+param['TextOffset']+hbox))
        if 'color' in g:
          gtexts[-1].SetTextColor(g['color'])
          arrows[-1].SetLineColor(g['color'])
        
      xmin = xmin + x_width + param['space']

    for line in alllines:
      line.Draw()

    for arrow in arrows:
      arrow.SetLineWidth(param['ArrowWidth'])
      arrow.SetArrowSize(param['ArrowSize'])
      arrow.SetAngle(param['ArrowAngle'])
      arrow.Draw(param['ArrowOption'])

    for box in boxes:
      box.SetFillColor(0)
      box.Draw()

    for text in gtexts:
      text.Draw()

    for line in dlines:
      line.SetLineWidth(param['LineWidth'])
      line.SetLineStyle(2)
      line.Draw()

    for text in ttexts:
      text.SetTextSize(param['TitleTextSize'])
      text.SetTextAlign(22)
      text.Draw()

    canv.Print(data['OutputFile'])

  canv.Print(data['OutputFile']+']')
