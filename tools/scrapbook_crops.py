from PIL import Image, ImageOps, ImageDraw, ImageFont
A="/mnt/user-data/attachments/bbefee32-b007-5e8f-8388-b57898708902/"
ids=[l.split('\t')[1] for l in open('pages.txt').read().split('\n')]
D=1.024  # displayed -> original (pages 24-46)
C={ # name: (page, (x0,y0,x1,y1), scale, rotate)
"tin-house-2009":(24,(385,795,1405,1485),D,0),
"news-2009-giving-kids-chance":(24,(340,45,988,592),D,0),
"clown-1990":(25,(150,30,380,640),D,0),
"kidz-club-1990-group":(25,(485,90,1030,485),D,0),
"kidz-club-1990-field":(25,(355,650,1220,1275),D,0),
"kidz-club-1990-puppet-show":(25,(340,1330,1185,1880),D,0),
"clowns-early-team":(26,(775,30,1440,770),D,0),
"kidz-club-early-outdoor-show":(26,(365,725,1210,1325),D,0),
"kidz-club-early-hall":(26,(385,1375,1235,1975),D,0),
"news-1999-jessica-kids":(27,(515,645,1415,1220),D,0),
"news-2000-millennium-party":(27,(505,1400,1415,1840),D,0),
"news-human-rights-day":(28,(55,80,942,495),D,0),
"back-to-school-hampers-bca":(28,(1018,2,1950,685),D,0),
"news-2014-graduation":(28,(925,870,1985,1315),D,0),
"news-ho-ho-ho":(29,(780,1430,1300,1800),D,0),
"news-2007-sports-day":(30,(108,700,758,1095),D,0),
"news-2007-grade-r-graduation":(30,(782,398,1872,1015),D,0),
"news-sewing-classes":(31,(190,1255,718,1655),D,0),
"news-2007-ballerinas":(32,(240,485,1345,1245),D,0),
"academy-opening-mural":(33,(215,15,1235,680),D,0),
"academy-opening-ribbon":(33,(215,680,1235,1335),D,0),
"academy-opening-guests":(33,(210,1340,1230,2000),D,0),
"news-festive-hampers":(34,(5,115,1080,765),D,0),
"concert-2012":(34,(1090,40,1980,700),D,0),
"christmas-2007-spin-da-flava":(34,(5,770,1000,1450),D,0),
"news-2008-nedbank-cheque":(35,(828,375,1848,1005),D,0),
"news-waffles-day":(36,(1308,368,1945,890),D,0),
"news-ballerinas-wednesday-club":(36,(88,842,958,1290),D,0),
"news-2007-trevor-40th":(37,(1035,350,1908,1130),D,0),
"news-2007-nair-family":(38,(1050,140,1925,1315),D,0),
"news-2008-youth-day-winners":(39,(200,410,850,840),D,0),
"youth-day-2008-crowd":(39,(145,840,850,1950),D,-90),
"news-2008-youth-day-ballet":(39,(850,1505,1255,1830),D,0),
"news-2007-spin-da-flava-kids":(40,(457,93,1557,622),D,0),
"christmas-2007-team":(40,(585,693,1610,1380),D,0),
"youth-camp-group":(41,(230,30,1250,670),D,0),
"youth-camp-obstacle":(41,(230,675,1250,1350),D,0),
"youth-camp-river":(41,(230,1355,1250,2000),D,0),
"gift-of-givers-children":(42,(232,15,1250,635),D,0),
"gift-of-givers-jessica":(42,(232,640,1250,1310),D,0),
"gift-of-givers-queue":(42,(232,1315,1250,1995),D,0),
"news-2006-heroes-cheque":(44,(205,225,1945,1380),D,0),
"news-2006-lighting-up-etete":(45,(50,15,870,1070),D,0),
"news-2006-thank-you-kids":(45,(875,440,1454,915),D,0),
"news-nkobongo-christmas":(46,(232,30,1428,560),D,0),
"news-standard-bank-toys":(46,(232,950,1430,1625),D,0),
"outreach-johannesburg-camp":(0,(244,44,1284,744),1,0),
"movie-day-kidz-club":(0,(324,772,1184,1364),1,0),
"fun-and-games-early":(1,(324,772,1184,1372),1,0),
"clothes-distribution-early":(1,(336,1412,1192,2004),1,0),
"outreach-early-gathering":(1,(244,52,1284,752),1,0),
"siza-water-puppet-booth":(3,(392,1452,1264,2032),1,0),
"early-outdoor-assembly":(3,(312,64,1352,764),1,0),
"clown-christmas-2000":(4,(1056,364,1424,956),1,0),
"kidz-club-banner-march":(4,(352,1372,1224,1972),1,0),
"christmas-2000-900-kids":(5,(232,732,1264,1344),1,0),
"christmas-2000-show":(5,(224,44,1264,676),1,0),
"outreach-hospital-children":(6,(204,56,1256,672),1,0),
"kidz-club-early-group-outside":(6,(224,704,1264,1392),1,0),
"puppets-early":(7,(344,744,1216,1344),1,0),
"christmas-1999-gifts":(7,(276,1372,1316,1952),1,0),
"outreach-shakaskraal":(8,(256,672,1296,1372),1,0),
"outreach-shakaskraal-clown":(8,(272,1444,1312,2032),1,0),
"food-distribution-collage":(9,(84,244,1912,1376),1,0),
"christmas-2001-crowd":(10,(932,116,1904,636),1,0),
"christmas-2002-collage":(13,(92,72,1864,1344),1,0),
"christmas-2003-shakashead":(14,(32,284,1932,1324),1,0),
"training-future-leaders":(15,(16,12,2044,704),1,0),
"christmas-2003-etete":(23,(132,244,1924,1344),1,0),
"christmas-2001-games":(21,(304,96,1172,704),1,0),
"news-2005-santa-visits-etete":(12,(130,350,900,970),1489/1018,0),
"news-2001-magic-of-christmas":(22,(380,200,1310,790),2048/1400,0),
"news-2002-shines-a-little-light":(19,(378,5,1305,600),2048/1400,0),
}
for n,(p,b,s,r) in C.items():
    im=ImageOps.exif_transpose(Image.open(A+ids[p]+"-image.jpg")).convert("RGB")
    W,H=im.size; bb=[int(v*s) for v in b]; bb=[max(0,bb[0]),max(0,bb[1]),min(W,bb[2]),min(H,bb[3])]
    c=im.crop(bb)
    if r: c=c.rotate(r,expand=True)
    c.save(f"crops/{n}.jpg",quality=92)
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
names=list(C); T=300
for s in range(0,len(names),20):
    ch=names[s:s+20]; sh=Image.new("RGB",(5*T,4*(T+22)),"white"); d=ImageDraw.Draw(sh)
    for i,n in enumerate(ch):
        im=Image.open(f"crops/{n}.jpg"); im.thumbnail((T-6,T-6)); x,y=(i%5)*T,(i//5)*(T+22)
        sh.paste(im,(x+3,y+3)); d.text((x+3,y+T),n[:34],fill="black",font=F)
    sh.save(f"cs-{s//20}.jpg",quality=72)
print(len(C))
