document.addEventListener("DOMContentLoaded", function () {

    const img   = document.getElementById('player');
    const svg   = document.getElementById('lines');
    const scene = document.querySelector('.scene');
    const NS    = 'http://www.w3.org/2000/svg';

    // ── Track list ───────────────────────────────────────────────
    // Add filenames here when you drop new tracks into assets/audio/
    const TRACKS = [
        'assets/audio/Subway Shy copy.m4a',
        'assets/audio/1-01 PLEASENT DAY.m4a',
    ];

    const audio     = new Audio();
    const tracklist = document.getElementById('tracklist');
    let   current   = 0;

    function trackName(path) {
        return path.split('/').pop().replace(/\.[^.]+$/, '');
    }

    function loadTrack(index) {
        current      = index;
        audio.src    = TRACKS[index];
        document.querySelectorAll('.track-item').forEach((el, i) => {
            el.classList.toggle('playing', i === index);
        });
    }

    // Build track list UI
    TRACKS.forEach((path, i) => {
        const btn = document.createElement('button');
        btn.className   = 'track-item';
        btn.textContent = trackName(path);
        btn.addEventListener('click', () => {
            loadTrack(i);
            audio.play();
        });
        tracklist.appendChild(btn);
    });

    loadTrack(0);

    // Show / hide tracklist with playback
    audio.addEventListener('play',  () => tracklist.classList.add('visible'));
    audio.addEventListener('pause', () => tracklist.classList.remove('visible'));
    audio.addEventListener('ended', () => {
        tracklist.classList.remove('visible');
        // auto-advance if more tracks
        if (current + 1 < TRACKS.length) {
            loadTrack(current + 1);
            audio.play();
        }
    });

    // Controls
    document.getElementById('label-play').addEventListener('click', () => audio.play());

    document.getElementById('label-stop').addEventListener('click', () => {
        audio.pause();
        audio.currentTime = 0;
    });

    // REW — hold to scrub backward
    let rewTimer = null;
    function rewStart() {
        if (rewTimer) return;
        rewTimer = setInterval(() => {
            audio.currentTime = Math.max(0, audio.currentTime - 0.4);
        }, 50);
    }
    function rewStop() {
        clearInterval(rewTimer);
        rewTimer = null;
    }
    const rewBtn = document.getElementById('label-rew');
    rewBtn.addEventListener('mousedown',  rewStart);
    rewBtn.addEventListener('touchstart', rewStart, { passive: true });
    rewBtn.addEventListener('mouseup',    rewStop);
    rewBtn.addEventListener('mouseleave', rewStop);
    rewBtn.addEventListener('touchend',   rewStop);

    // FF — hold to play at 3× speed
    let ffTimer = null;
    function ffStart() {
        if (ffTimer) return;
        audio.playbackRate = 3;
        ffTimer = true;
    }
    function ffStop() {
        audio.playbackRate = 1;
        ffTimer = null;
    }
    const ffBtn = document.getElementById('label-ff');
    ffBtn.addEventListener('mousedown',  ffStart);
    ffBtn.addEventListener('touchstart', ffStart, { passive: true });
    ffBtn.addEventListener('mouseup',    ffStop);
    ffBtn.addEventListener('mouseleave', ffStop);
    ffBtn.addEventListener('touchend',   ffStop);

    // ── Button positions (image fractions) ───────────────────────
    const BTNS = {
        stop: { fx: 0.6409, fy: 0.5462 },
        play: { fx: 0.6875, fy: 0.5295 },
        rew:  { fx: 0.7295, fy: 0.5163 },
        ff:   { fx: 0.7705, fy: 0.5032 },
    };

    // ── Label positions (scene px, set by calibration) ───────────
    const LABEL_POS = {
        stop: { px: 1151.0, py: 397.0 },
        play: { px: 1003.0, py: 101.0 },
        rew:  { px: 1064.0, py: 130.0 },
        ff:   { px: 1119.0, py: 194.0 },
    };

    // ── Calibration mode ─────────────────────────────────────────
    const CALIBRATE = false;  // set to true to re-calibrate

    if (CALIBRATE) {
        const order  = ['STOP', 'PLAY', 'REW', 'FF'];
        const clicks = [];

        const hud = document.createElement('div');
        hud.style.cssText = `
            position: fixed; top: 16px; right: 16px;
            background: rgba(255,255,255,0.92);
            border: 1px solid #000;
            padding: 12px 16px;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            line-height: 1.8;
            z-index: 999;
            min-width: 240px;
            pointer-events: none;
        `;
        hud.innerHTML = `Click where you want the <b>${order[0]}</b> label`;
        document.body.appendChild(hud);

        document.addEventListener('click', function (e) {
            if (clicks.length >= order.length) return;
            const sr = scene.getBoundingClientRect();
            const px = (e.clientX - sr.left).toFixed(1);
            const py = (e.clientY - sr.top).toFixed(1);
            clicks.push({ name: order[clicks.length], px, py });
            const next = order[clicks.length];
            const log  = clicks.map(c => `${c.name}: px=${c.px}, py=${c.py}`).join('<br>');
            hud.innerHTML = next
                ? `${log}<br><br>Click where you want the <b>${next}</b> label`
                : `${log}<br><br><b>Done — paste these to Claude</b>`;
        });

        return;
    }

    // ── Draw ─────────────────────────────────────────────────────
    function draw() {
        const sr = scene.getBoundingClientRect();
        const ir = img.getBoundingClientRect();

        svg.setAttribute('width',  sr.width);
        svg.setAttribute('height', sr.height);
        svg.innerHTML = '';

        function btnPt(fx, fy) {
            return {
                x: (ir.left - sr.left) + fx * ir.width,
                y: (ir.top  - sr.top)  + fy * ir.height,
            };
        }

        const pts = {
            stop: btnPt(BTNS.stop.fx, BTNS.stop.fy),
            play: btnPt(BTNS.play.fx, BTNS.play.fy),
            rew:  btnPt(BTNS.rew.fx,  BTNS.rew.fy),
            ff:   btnPt(BTNS.ff.fx,   BTNS.ff.fy),
        };

        // Place labels at calibrated positions
        function placeLabel(id, x, y) {
            const el = document.getElementById(id);
            el.style.left      = x + 'px';
            el.style.top       = y + 'px';
            el.style.transform = 'translate(-50%, -50%)';
            el.style.bottom    = '';
            el.style.right     = '';
        }

        placeLabel('label-stop', LABEL_POS.stop.px, LABEL_POS.stop.py);
        placeLabel('label-play', LABEL_POS.play.px, LABEL_POS.play.py);
        placeLabel('label-rew',  LABEL_POS.rew.px,  LABEL_POS.rew.py);
        placeLabel('label-ff',   LABEL_POS.ff.px,   LABEL_POS.ff.py);

        requestAnimationFrame(() => {
            svg.innerHTML = '';

            function labelCenter(id) {
                const r = document.getElementById(id).getBoundingClientRect();
                return {
                    x: (r.left + r.right)  / 2 - sr.left,
                    y: (r.top  + r.bottom) / 2 - sr.top,
                };
            }

            const pairs = [
                ['stop', 'label-stop'],
                ['play', 'label-play'],
                ['rew',  'label-rew'],
                ['ff',   'label-ff'],
            ];

            pairs.forEach(([key, labelId]) => {
                const p1 = pts[key];
                const p2 = labelCenter(labelId);

                // Stop the line 14px short of the label center
                const dx  = p2.x - p1.x;
                const dy  = p2.y - p1.y;
                const len = Math.sqrt(dx * dx + dy * dy);
                const endX = p2.x - (dx / len) * 14;
                const endY = p2.y - (dy / len) * 14;

                const line = document.createElementNS(NS, 'line');
                line.setAttribute('x1', p1.x);
                line.setAttribute('y1', p1.y);
                line.setAttribute('x2', endX);
                line.setAttribute('y2', endY);
                line.setAttribute('stroke', '#000');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);

                const dot = document.createElementNS(NS, 'circle');
                dot.setAttribute('cx', p1.x);
                dot.setAttribute('cy', p1.y);
                dot.setAttribute('r', '3');
                dot.setAttribute('fill', '#000');
                svg.appendChild(dot);
            });
        });
    }

    if (img.complete) {
        draw();
    } else {
        img.addEventListener('load', draw);
    }

    window.addEventListener('resize', draw);
});
