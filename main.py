import yt_dlp
import whisper
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import textwrap
from langchain import OpenAI, LLMChain
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain

def download_mp4_from_youtube(url):
    # Set the options for the download
    filename = 'lecuninterview.mp4'
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': filename,
        'quiet': True,
    }

    # Download the video file
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
    


if __name__ == '__main__':
    # Define the url with desired youtube video link
    url = "https://www.youtube.com/watch?v=mBjPyte2ZZo"
    
    # Download the video
    download_mp4_from_youtube(url)
    
    # Use whisper and save the transcription to a file
    model = whisper.load_model("base")
    result = model.transcribe("lecuninterview.mp4")
    with open ('text.txt', 'w') as file:  
        file.write(result['text'])
    
    # Intialize the LLM
    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # Intialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=0, separators=[" ", ",", "\n"]
    )
    
    # Read the text file
    with open('text.txt') as f:
        text = f.read()

    # Split the text and make documents
    texts = text_splitter.split_text(text)
    docs = [Document(page_content=t) for t in texts[:4]]
    
    prompt_template = """Write a concise bullet point summary of the following:


    {text}


    CONSCISE SUMMARY IN BULLET POINTS:"""

    BULLET_POINT_PROMPT = PromptTemplate(template=prompt_template, 
                            input_variables=["text"])
    
    # load the summarize chain with map_reduce type
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=BULLET_POINT_PROMPT)

    # Run the chain
    output_summary = chain.run(docs)
    
    # Get the output in wrapped form
    wrapped_text = textwrap.fill(output_summary, width=100, break_long_words=False, replace_whitespace=False)
    print(wrapped_text)


