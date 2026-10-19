// Original, deterministic vector artwork. Concept only; not a field simulation.
import { writeFile } from 'node:fs/promises';
const rings = Array.from({length: 13}, (_, n) => {
  const spread = 45 + n * 13;
  return `<path d="M 294 190 C ${320-spread*1.25} 222, ${320-spread*1.65} 369, 296 435 M 346 190 C ${320+spread*1.25} 222, ${320+spread*1.65} 369, 344 435"/>`;
}).join('');
const windings = Array.from({length: 19}, (_, n) => {
  const y = 155 + n * 4;
  return `<path d="M240 ${y} C240 ${y+29} 400 ${y+29} 400 ${y}" fill="none" stroke="url(#copper)" stroke-width="4.2"/><path d="M243 ${y} C243 ${y+25} 396 ${y+25} 396 ${y}" fill="none" stroke="#efbb8b" stroke-opacity=".35" stroke-width=".8"/>`;
}).join('');
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="620" viewBox="0 0 640 620">
<defs>
<radialGradient id="back"><stop stop-color="#fafbf7"/><stop offset="1" stop-color="#edf0ea"/></radialGradient>
<linearGradient id="copper"><stop stop-color="#70422e"/><stop offset=".2" stop-color="#af6c43"/><stop offset=".45" stop-color="#edbc8c"/><stop offset=".65" stop-color="#ce9466"/><stop offset="1" stop-color="#71472f"/></linearGradient>
<linearGradient id="core"><stop stop-color="#515f55"/><stop offset=".4" stop-color="#a3aca0"/><stop offset=".65" stop-color="#d1d6cd"/><stop offset="1" stop-color="#647265"/></linearGradient>
<radialGradient id="ball" cx="32%" cy="24%" r="80%"><stop stop-color="#f4f2e5"/><stop offset=".19" stop-color="#c7d0bc"/><stop offset=".45" stop-color="#798d75"/><stop offset=".78" stop-color="#354c3c"/><stop offset="1" stop-color="#172f23"/></radialGradient>
<radialGradient id="shadow"><stop stop-color="#6e7d67" stop-opacity=".23"/><stop offset="1" stop-color="#6e7d67" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".65" fill="#97a490" opacity=".32"/></pattern>
</defs>
<rect width="640" height="620" fill="url(#back)"/><rect x="30" y="70" width="580" height="500" fill="url(#grid)"/>
<circle cx="320" cy="320" r="219" fill="none" stroke="#aab7a3" stroke-opacity=".22"/>
<path d="M320 75V555M70 320H570" stroke="#aab7a3" stroke-opacity=".28" stroke-dasharray="3 7"/>
<g stroke="#879c7d" stroke-width="1" fill="none" opacity=".45">${rings}</g>
<ellipse cx="320" cy="520" rx="111" ry="22" fill="url(#shadow)"/>
<path d="M285 88H355V167H285Z" fill="url(#core)"/><ellipse cx="320" cy="88" rx="35" ry="9" fill="#bbc3b6"/>
<path d="M238 153V228C238 263 402 263 402 228V153Z" fill="url(#copper)"/>
${windings}
<ellipse cx="320" cy="151" rx="82" ry="24" fill="#ab7049"/><ellipse cx="320" cy="151" rx="38" ry="11" fill="#53634f"/><path d="M285 111H355V150C355 163 285 163 285 150Z" fill="url(#core)"/>
<ellipse cx="320" cy="253" rx="49" ry="13" fill="#485a47"/><path d="M271 243V263C271 279 369 279 369 263V243" fill="url(#core)"/><ellipse cx="320" cy="263" rx="49" ry="13" fill="#71816b"/>
<path d="M400 184C447 184 458 147 473 122" fill="none" stroke="#986846" stroke-width="3"/>
<circle cx="320" cy="406" r="48" fill="url(#ball)"/><path d="M287 383C298 365 322 362 337 371" fill="none" stroke="#f0f3e7" stroke-width="2" opacity=".55"/>
<path d="M386 276H425M374 358H425M416 282V352" stroke="#8b6b53" stroke-width="1" fill="none"/>
<path d="M412 288L416 280L420 288M412 346L416 354L420 346" fill="none" stroke="#8b6b53"/>
<g fill="#65725f" font-family="-apple-system,Segoe UI,sans-serif" font-size="10" letter-spacing="1.2"><text x="432" y="321">x</text><text x="432" y="337" font-size="8" letter-spacing=".6">AIR GAP</text><text x="65" y="182" font-size="8">ELECTROMAGNET</text><text x="65" y="429" font-size="8">MAGNETIC OBJECT</text></g>
<path d="M158 179H215L238 194M162 426H251L273 412" fill="none" stroke="#a3af9a" stroke-width=".8"/>
<g stroke="#9d6847" fill="none" stroke-width="1.3"><path d="M320 334V302M316 308L320 301L324 308M320 474V495M316 489L320 496L324 489"/></g>
</svg>`;
await writeFile(new URL('../assets/field.svg', import.meta.url), svg);
console.log('Created assets/field.svg (concept illustration).');
