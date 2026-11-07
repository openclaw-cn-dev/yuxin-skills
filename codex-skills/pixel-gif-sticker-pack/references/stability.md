# Visual stability for character actions

Use when generating consecutive actions or repairing choppy/frame-skipping playback. Also inspect individual drawings for visual defects. Applies across illustration and photographic styling; it does not force every light-motion sticker into frame-by-frame generation.

## Anchor before expanding

1. Choose an accepted identity reference and list visible invariants: head silhouette, eye size/spacing, nose/mouth position, hair/accessories, costume panels, buttons/bows, limb and hand type. State permitted changes separately: blink, smile, turn, body lean, gesture.
2. For a new or unstable character/action, generate a small model sheet of roughly 3–4 key poses: neutral, anticipation, peak, settling. Check these at useful face size first. Reference the reviewed sheet while generating transitions. Do not commit to a large pack before the pilot is acceptable.
3. Plan a coherent short action. For full-character acting, 12–16 drawings can be a useful starting point; more frames are not an acceptance criterion. Keep the head/torso participating, camera and scale fixed, and clothing construction unchanged. Start with restrained mouth opening/turning when big changes have caused drift.

Character-specific examples, not universal face templates:

- Anya: keep the rounded cheek/chin contour, eye spacing and green irises stable. Separate hands from collar/face; check fingers throughout heart formation, not only the completed heart. Keep hair ornaments and gold trim consistent. A closed-eye smile should not squash the face.
- Doraemon: keep round head diameter and head/body ratio stable, one nose/bell/pouch, three whiskers per cheek, round hands without human fingers and correctly attached feet. Check mouth size and the nose-to-mouth center line as the head moves; a broad smile must not turn the head into an egg.

Natural expression changes are allowed. Do not stabilize by pasting one frozen face over every frame or by replacing full-character acting with an isolated rotating arm.

## Temporal continuity first

When the user reports “抽帧”, interpret it as choppy motion or apparently missing transitions, not automatically as an unattractive still. Inspect pose-to-pose increments, uneven holds, camera/grid jumps and the loop seam. Fill missing action stages using the neighboring poses; correct layout errors before redrawing. Increasing playback FPS, repeating identical frames or crossfading alone does not supply missing physical motion.

Removing a malformed isolated pose may be a separate visual repair, but it is not a fix for choppiness by itself. Do not remove valid in-betweens or add long holds to claim a smoother action; review the resulting cadence and disclose any remaining gap.

## Inspect the delivered GIF, not just the source sheet

```sh
python3 scripts/review_gif.py extract build/GIF合集/action.gif build/review/action --focus 150 80 360 280
```

The optional focus box is in final GIF pixel coordinates `(left top right bottom)`. Choose it for that character; do not blindly reuse the example. The tool saves every decoded frame, a native-size numbered sheet, optional face detail sheet, a browser player with the actual GIF and frame stepping, a technical audit and a pending `review.json`.

- Inspect **every** numbered frame for identity, head shape, eyes/mouth, hands/occlusions, costume and stray pieces from adjacent atlas cells. Native-size inspection matters; a tiny grid can hide defects.
- Watch normal playback and step through suspicious transitions. Inspect first→last→first too. A collection of attractive stills can still flash or jump when animated. A slow player is helpful for repairs but does not replace normal-speed playback.
- The tool's transition scores only nominate frames to inspect. A valid blink can score high; a malformed face can score low. Never fill visual approvals from those scores or from distinct-frame counts.
- Label technical status, assistant visual review and user acceptance separately. Without playback access, leave playback pending and explain the limit. A new