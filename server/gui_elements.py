from flask import Flask, render_template

from server import *

@app.route("/")
def main():
    return render_template('miner.html')
