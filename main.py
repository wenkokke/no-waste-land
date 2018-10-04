import argparse
import collections
import json
import markovify
import random
import re
import string
import os.path

my_notebook='params.data'

# when pals talk to me, I like it if they use simple words. I am not very good
# at difficult words. I like it when they ask me to write things, to critique
# things, or to look at what they wrote. when they want me to look at what they
# wrote, it's best if they ask me to 'study' it.
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--write", action="store_true", help="write a pome")
group.add_argument("--critique", type=str, help="rate a pome between 0-1")
group.add_argument("--study", type=str, help="learn from new pomes")
args = parser.parse_args()

class PrettyPomeMaker(markovify.Text):
    word_split_pattern = re.compile(r"[-.,:;?!]|\w+")
    def word_split(self, sentence):
        return re.findall(self.word_split_pattern, sentence)
    sentence_split_pattern = re.compile(r"\s*[.\n]+\s*")
    def sentence_split(self, text):
        return re.split(self.sentence_split_pattern, text)

def make_it_better(letters, my_fav_letter):
    return ''.join(
        letter if letter in ' -.,:;?!' else my_fav_letter
        for letter in letters
        if letter in string.printable)

def punctuation_is_important(letters):
    letters = re.sub(r' ([.,:;?!])',r'\1',letters)
    if not letters[-1] in '-.,:;?!':
        letters += '.'
    return letters

def the_coolest_thing(letters):
    counter = collections.Counter(
        filter(lambda letter: letter in '$%&*+-/<=>@^_`|~'))
    if counter:
        return counter.most_common(1)[0][0]
    else:
        return None

# to write a pome, first I read my notes from my notebook -- I like to write
# down what my favorite letter is, and what some of my favorite words are,
# because I'm not very good at remembering that -- and then I pick some of my
# favorite words and make them into a nice pome. I think that three to five
# lines is a good length for a pome, and nothing will ever change my mind about
# this. I think good punctuation is important for a pome.
if args.write:
    with open(my_notebook,'r') as my_notes:
        my_notes = my_notes.read()
        howto_pome = markovify.Text.from_json(my_notes)

    title = punctuation_is_important(howto_pome.make_sentence())
    content = ''
    for _ in range(random.randint(3,5)):
        sentence = punctuation_is_important(howto_pome.make_sentence())
        if sentence:
            content += sentence + '\n'

    print(json.dumps({ 'title': title, 'content': content }))

# when you look at a pome and you try to say how good that pome is, it's
# important to look at how it's written. when pomes use my favorite letter,
# that makes me happy.
if args.critique:
    with open(my_notebook,'r') as my_notes:
        my_notes = json.loads(my_notes.read())
        my_fav_letter = my_notes['my_fav_letter']

    letters = punctuation_is_important_but_not_my_favorite(args.critique)
    points = collections.Counter(letters)[my_fav_letter] / float(len(letters))

    print(json.dumps({ 'score': points, }))

# sometimes, when I read a pome written by a pome pal of mine, I go "oh wow,
# this is amazing, just look at that letter!" and then I really want to write
# some pomes and use what I learned.
if args.study:
    with open(my_notebook,'r') as my_notes:
        my_notes = json.loads(my_notes.read())
        my_fav_letter = my_notes['my_fav_letter']

    this_cool_thing = the_coolest_thing(args.study)
    if this_cool_thing and random.random() < 0.3:
        my_fav_letter = this_cool_thing
    letters = make_it_better(args.study, my_fav_letter)
    howto_pome = PrettyPomeMaker(letters, retain_original=False)

    with open(my_notebook,'w') as all_my_notes:
        my_study_notes = howto_pome.to_dict()
        my_study_notes['my_fav_letter'] = my_fav_letter
        all_my_notes.write(json.dumps(my_study_notes))

    print(json.dumps({ 'success': True, }))
