# They Once Existed · A Gift from the Gods

Open `新游戏-English.html` in Chrome or Edge to play the English edition. Choose **Begin** on the title screen, then select the Boar, Cat, or Duck. Each character has two endings, for six in total. Observation, exploration, and sharing choices remain available along the way.

The title, story, dialogue, choices, journal, fact cards, accessibility labels, and interaction messages are in English. The English edition uses the same artwork, music, animal calls, monochrome themes, and animated text as the Chinese edition. The Boar and Duck routes have black backgrounds; the Cat route has a white background.

The HTML is self-contained apart from its media: images and audio load from the existing GitHub raw URLs. You can move or share the HTML file on its own. An internet connection with access to GitHub's raw file service is required.

## Controls

- Click a button to continue. Where indicated, you can also click the illustration.
- Click underlined text to change it or look closer. Click a typing line to reveal the whole sentence.
- Click an animal on the title or character screen to hear its call.
- **Home** returns to the title, **Cast** opens character selection, and **Journal** shows your endings.
- The Boar's charge requires five strikes. Hold the mist button for about two seconds; releasing it keeps your progress. You can also hold Space or Enter.
- During the Duck's scramble, alternate between the left and right ducks for six successful pushes.
- On small screens, use the tabs to switch between fact cards or character journals. The complete page fits the window without scrolling.

## Sound and progress

Music begins after your first click or key press. Use **Sound: on/off** to control music and sound effects. The title's music button can also turn sound back on.

The title and character screen use the original game's opening track, **Hollow Knight**. All six final endings and the journal use its closing track, **かたわれ時**. Chapter audio and animal calls keep their existing assignments. A track continues across pages that share it; changing chapters switches tracks.

Ending records and the sound setting are saved in this browser. The English edition has its own save key (`they-once-existed-new-gift-en-v1`) and Twine IFID. Clearing browser data, changing browsers, or using a private window affects these records.

## Editing and rebuilding

Import `新游戏-English.html` or `新游戏-English.twee` into Twine using **Harlowe 3.3.9**. The English edition uses English passage names and a separate IFID so it can be imported alongside the Chinese edition.

With Python 3 and Pillow available, run:

```powershell
python 制作/build_en.py
```

- `制作/build_en.py` contains the English story and Harlowe macros.
- `制作/game-en.css` adapts the shared layout for English typography.
- `制作/english_ui.py` translates the shared script's interface messages and CSS hints.
- `制作/game.css` and `制作/game.js` supply the shared layout, interactions, and audio.

Keep the existing local artwork and `制作/harlowe-3.3.9.json` when rebuilding. The generated HTML and Twee continue to reference media hosted on GitHub.
