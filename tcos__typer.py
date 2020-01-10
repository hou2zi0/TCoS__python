import requests as rq
import pandas as pd
import json
import sys
import typer
import spacy
import re
from tqdm import tqdm
import matplotlib.pyplot as plt

def handle(
            text: str,
            string: bool = typer.Option(False, "--string", "-s", help="Specifies the argument TEXT as being a string."),
            file: bool = typer.Option(False, "--file", "-f", help="Specifies the argument TEXT as being a file path."),
            wiki_url: bool = typer.Option(False, "--wikipedia-url", "-wiki", help="Specifies the argument TEXT as being a wikipedia article url."),
            plot: bool = typer.Option(False, "--plot", "-p", help="Produces a simple plot."),
            calculate_skewedness: bool = typer.Option(False, "--calculate_skew", "-cs", help="Calculates and outputs the skew of a distribution."),
            word_length_frequency_distribution: bool = typer.Option(False, "--word_length", "-wlfd", help="Calculates a frequency distribution of the given text’s words’ length."),
            punctuation_frequency_distribution: bool = typer.Option(False, "--punctuation", "-pfd", help="Calculates a frequency distribution of the given text’s punctuation.")
            ):
    if file:
        with open(f'{text}', 'r', encoding=utf8) as f:
            input_text = f.read()
    elif string:
        input_text = text
    elif wiki_url:
        res = rq.get(text)
        if res.status_code == 200:
            input_text = re.sub(r'\[[0-9]{1,5}\]', '', re.sub('<.*?>','',re.sub('<script.*?>.*?</script>','',res.text[re.search(r'<div id="mw-content-text".*?>',res.text).end():re.search(r'<h2.*?.>See also',res.text).start()])))
        else:
            typer.Exit(f'Could not fetch text from url. Status code was {res.status_code}.')
    else:
        input_text = text



    nlp = spacy.load('en')
    with tqdm() as pbar:
        doc = nlp(input_text)

    if word_length_frequency_distribution:
        frequency_distribution = { str(i): 0 for i in range(1, 31) }
        with tqdm(total=len(doc)) as pbar:
            for token in doc:
                if token.is_alpha:
                    frequency_distribution[str(len(token))] += 1
                pbar.update(1)
        df = pd.DataFrame.from_dict(
                frequency_distribution,
                orient='index',
                columns=['count']
                )
        print(df)
        plot_data(df, plot)
        caculate_skew(df, calculate_skewedness)
    if punctuation_frequency_distribution:
        punctuation_tokens = [ token for token in doc if token.is_punct ]
        frequency_distribution = { str(i): 0 for i in punctuation_tokens }
        with tqdm(total=len(punctuation_tokens)) as pbar:
            for token in punctuation_tokens:
                    frequency_distribution[str(token)] += 1
                    pbar.update(1)
        df = pd.DataFrame.from_dict(
                frequency_distribution,
                orient='index',
                columns=['count']
                )
        print(df)
        plot_data(df, plot)
        caculate_skew(df, calculate_skewedness)


def caculate_skew(df, calculate_skewedness):
    if calculate_skewedness:
        output = ''
        skews = df.skew()
        for index, skew in enumerate(skews):
            if skew > 0:
                skew_type = 'positive'
                tail_orientation = 'The distribution’s tail is oriented to the right.'
            elif skew < 0:
                skew_type = 'negative'
                tail_orientation = 'The distribution’s tail is oriented to the left.'
            else:
                skew_type = false
                tail_orientation = 'The distribution has no tail, since the distribution is symmetrical.'
            output += f"""
Column {df.columns[index].upper()}
The distribution’s skew is {skew}.
The skew’s type is {skew_type}.
{tail_orientation}
"""
        print(output)

def plot_data(df, plot):
    if plot:
        plot_type = typer.prompt("Specify plot type (bar, line):")
        if plot_type in ['bar', 'line']:
            df.plot(kind = plot_type)
            plt.show()
        else:
            typer.Exit('Unknown plot type. Available plot types are "bar", "line".')




if __name__ == "__main__":
    typer.run(handle)