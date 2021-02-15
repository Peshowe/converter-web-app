# Ivanchevski spelling converter web app

A Django web app whose main functionality is converting text from the modern Bulgarian spelling into the historic Ivanchevski spelling.

The web app is currently hosted here: https://pravopis.osvedomitel.bg/

## Spelling converter logic
The main spelling conversion logic is in [converter/converter.py](converter/converter.py), with some helper logic in [converter/process_vocabs.py](converter/process_vocabs.py) and [converter/pos_tagger.py](converter/pos_tagger.py). 

### POS tagging using BERT
For some cases, we need part-of-speech (POS) tagging to determine the correct spelling of a given word. 
For this purpose we use a multilingual BERT model fine-tuned for POS tagging on the Bulgarian language (The dataset used for training is the one provided by [Bulgarian Tree Bank](http://bultreebank.org/bg/)).

The trained weights are not included in the repo, since they're a little too big. For now I've uploaded them [here](https://drive.google.com/file/d/1-6gDERt66MUBYs3-wDtIRxR3V2y2t5sr/view?usp=sharing). They should go into `converter/static/converter/bert_model/bert_last_epoch.h5`. 
If they're not provided, the app will still work, but not do POS tagging.


### Running locally

To run locally, you'd need to create a secrets.py file in the [converter_web_app](converter_web_app) directory where a SECRET_KEY variable is defined with a random string that Django can use for a secret key. 

Then just install dependencies and run the Django dev server

```
pip install -r requirements.py
python manage.py runserver
```

## References

For the POS tagging using BERT, a lot of code was reused from this repo: https://github.com/soutsios/pos-tagger-bert

For the certbot integration, I used the approach described here: https://github.com/wmnnd/nginx-certbot

## License
All code in this repository is licensed under the terms of the `MIT License`. For further information please refer to the `LICENSE.md` file.