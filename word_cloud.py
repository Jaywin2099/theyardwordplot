from prepare import clean
from os import path, listdir
import wordcloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

num_samples = 2000
test = 6

def plot_word_cloud(wc):
    plt.imshow(wc)
    plt.axis("off")
    plt.show()
    plt.savefig(path.join("wordclouds", f"test{test}.png"))

text = ""

i = 0
for file in listdir("subtitles"):
    if i >= num_samples:
        break
    p = path.join("subtitles", file)
    print(f"Reading {p}...")

    with open(p, "r") as f:
        text += " " + f.read()

    i += 1

text = clean(text)

with open("text.txt", "w") as f:
    f.write(text)
    f.close()


''' masking the yard logo eventually
wc.background_color = "white"
yard_mask = np.array(Image.open('./yardlogo.jpg'))

wc = wordcloud.WordCloud(background_color = 'white', mask = yard_mask, contour_width = 2, contour_color = 'black').generate(text)
'''

print("Generating word cloud...")

wc = wordcloud.WordCloud()
wc.width = 4500
wc.height = 4500
wc.max_words = 600
img = wc.generate(clean(text))

print(img.words_)

print("Plotting word cloud...")
plot_word_cloud(img)

input("Press Enter to continue...")