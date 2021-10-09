LZSS_OFFSET_BIT_COUNT=9
LZSS_LENGTH_BIT_COUNT=4



def encode(dt):
	v=0
	bc=64
	bf=bytearray(1<<(LZSS_OFFSET_BIT_COUNT+1))
	for i in range(0,(1<<LZSS_OFFSET_BIT_COUNT)-(1<<LZSS_LENGTH_BIT_COUNT)-1):
		bf[i]=0
	dti=0
	i=(1<<LZSS_OFFSET_BIT_COUNT)-(1<<LZSS_LENGTH_BIT_COUNT)-1
	r=i
	while (i<(1<<(LZSS_OFFSET_BIT_COUNT+1))):
		if (dti==len(dt)):
			break
		bf[i]=dt[dti]
		i+=1
		dti+=1
	o=b""
	while (r<i):
		s=0
		l=1
		c=bf[r]
		mn=i-r
		if (mn>(1<<LZSS_LENGTH_BIT_COUNT)+1):
			mn=(1<<LZSS_LENGTH_BIT_COUNT)+1
		for j in range(r-((1<<LZSS_OFFSET_BIT_COUNT)-(1<<LZSS_LENGTH_BIT_COUNT)-1),r):
			if (bf[j]==c):
				k=1
				while (k<mn and bf[j+k]==bf[r+k]):
					k+=1
				if (k>l):
					s=j
					l=k
		e=None
		el=None
		if (l==1):
			e=256|c
			el=9
		else:
			e=((s&((1<<LZSS_OFFSET_BIT_COUNT)-1))<<LZSS_LENGTH_BIT_COUNT)|(l-2)
			el=LZSS_OFFSET_BIT_COUNT+LZSS_LENGTH_BIT_COUNT+1
		if (el>15):
			raise RuntimeError
		if (bc<el):
			v=(v<<bc)|(e>>(el-bc))
			o+=bytearray([(v>>56)&0xff,(v>>48)&0xff,(v>>40)&0xff,(v>>32)&0xff,(v>>24)&0xff,(v>>16)&0xff,(v>>8)&0xff,v&0xff])
			v=e
			bc+=64-el
		else:
			v=(v<<el)|e
			bc-=el
		r+=l
		if (r>=(1<<(LZSS_OFFSET_BIT_COUNT+1))-(1<<LZSS_LENGTH_BIT_COUNT)-1):
			for j in range(0,1<<LZSS_OFFSET_BIT_COUNT):
				bf[j]=bf[j+(1<<LZSS_OFFSET_BIT_COUNT)]
			i-=1<<LZSS_OFFSET_BIT_COUNT
			r-=1<<LZSS_OFFSET_BIT_COUNT
			while (i<(1<<(LZSS_OFFSET_BIT_COUNT+1))):
				if (dti==len(dt)):
					break
				bf[i]=dt[dti]
				i+=1
				dti+=1
	if (bc!=64):
		v<<=bc
		o+=bytearray([(v>>56)&0xff,(v>>48)&0xff,(v>>40)&0xff,(v>>32)&0xff,(v>>24)&0xff,(v>>16)&0xff,(v>>8)&0xff,v&0xff])
	return o



def decode(dt,ol):
	bf=bytearray(1<<LZSS_OFFSET_BIT_COUNT)
	r=0
	while (r<(1<<LZSS_OFFSET_BIT_COUNT)-(1<<LZSS_LENGTH_BIT_COUNT)-1):
		bf[r]=0
		r+=1
	v=0
	bc=0
	dti=0
	i=0
	o=bytearray(ol)
	while (i<ol):
		if (bc==0):
			if (dti+8>=len(dt)):
				raise RuntimeError
			v=(dt[dti]<<56)|(dt[dti+1]<<48)|(dt[dti+2]<<40)|(dt[dti+3]<<32)|(dt[dti+4]<<24)|(dt[dti+5]<<16)|(dt[dti+6]<<8)|dt[dti+7]
			bc=64
			dti+=8
		bc-=1
		e=0
		el=(8 if v&(1<<bc) else LZSS_OFFSET_BIT_COUNT+LZSS_LENGTH_BIT_COUNT)
		if (bc<el):
			e=(v&((1<<bc)-1))<<(el-bc)
			if (dti+8>len(dt)):
				raise RuntimeError
			v=(dt[dti]<<56)|(dt[dti+1]<<48)|(dt[dti+2]<<40)|(dt[dti+3]<<32)|(dt[dti+4]<<24)|(dt[dti+5]<<16)|(dt[dti+6]<<8)|dt[dti+7]
			bc=64-(el-bc)
			e|=v>>bc
			dti+=8
		else:
			bc-=el
			e=(v>>bc)&((1<<el)-1)
		if (el==8):
			o[i]=e
			bf[r]=e
			i+=1
			r=(r+1)&((1<<LZSS_OFFSET_BIT_COUNT)-1)
		else:
			k=e>>LZSS_LENGTH_BIT_COUNT
			e=k+(e&((1<<LZSS_LENGTH_BIT_COUNT)-1))+2
			while (k<e):
				o[i]=bf[k&((1<<LZSS_OFFSET_BIT_COUNT)-1)]
				bf[r]=o[i]
				i+=1
				r=(r+1)&((1<<LZSS_OFFSET_BIT_COUNT)-1)
				k+=1
	return bytes(o)



a=b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. In a feugiat mauris, in ultrices velit. Vestibulum in orci lacus. Curabitur a molestie leo. Sed in magna tincidunt, maximus purus a, sollicitudin lacus. Suspendisse potenti. Vestibulum imperdiet leo convallis maximus vulputate. Duis id elit sed diam facilisis ullamcorper. Mauris mattis aliquet nibh, vel dignissim mi dignissim in. Praesent sed iaculis arcu, et vehicula augue. Aliquam cursus ligula nisi, vitae vestibulum eros elementum id. Vestibulum commodo massa elit, non porta nibh lobortis sit amet. Duis ullamcorper placerat elit. Integer vel lectus purus. Maecenas non est orci. Aliquam lorem justo, aliquet id magna eu, suscipit feugiat diam. Nam eros sapien, posuere a nibh at, vulputate tincidunt tortor."
print(a)
b=encode(a)
print(b)
c=decode(b,len(a))
print(c)
print(len(c),len(b))
