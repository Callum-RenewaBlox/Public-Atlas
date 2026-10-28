/* Each step of WHAT_WE_NEED (what_we_need.js) opened up: what is needed, why,
   and how we know it is done. Same order as the steps there, and shown with them
   on the "What we need" tab of both views. app_srv_electrical.py inlines this
   file into both pages' data script, so edit it here only, and keep it plain
   data (no closing script tag, no HTML comment opener).

   Each "needed" item lists the places it points at (its marks). Both views put
   the item's number at each of those places, on the single-line diagram and in
   the site model, and STEP_MARKS gives each place the short name the site view
   labels it with. */
const STEP_MARKS = {
  'tie-acb':        'Tie ACB, 1250 A',
  'dc-acb':         'Data centre ACB, 1250 A',
  'busbar':         'Shared busbar',
  'rack-mccbs':     'Rack MCCBs, 2 × 400 A',
  'uvr':            'UVR coils',
  'cool-cdu':       'Cooler and CDU breakers',
  'gen-breaker':    'Generator breaker (2G)',
  'trip-cable':     'Control cable from the 2G container',
  'trip-relay':     'Interposing relay',
  'controller':     'Our controller',
  'watchdog':       'Watchdog relay',
  'incomer-cts':    'Split-core CTs',
  'boundary-meter': 'Boundary meter',
  'dc-meter':       'MID meter, data centre feed',
  'chp-meter':      'Multifunction meter, CHP incomer',
  'marshalling':    'Marshalling section',
  'ethernet':       'Ethernet switch',
  'ups':            'UPS-backed 230 V supply',
  'local-remote':   'Local/remote switch',
  'sld':            'Single-line diagram',
  'kiosk-plan':     'Kiosk plan',
  'fault':          'Fault fed by grid and engine together',
};

const STEPS_EXPLAINED = [
  { /* 1 Remove the mechanical interlock */
    needed: [
      { text: "Leave the mechanical interlock off the two 1250 A ACBs: the tie to the existing board and the data centre feed.", marks: ['tie-acb', 'dc-acb'] },
      { text: "Make both ACBs normally closed, so the existing board, the new board and the data centre section run as one busbar.", marks: ['busbar'] },
      { text: "Keep each ACB as a point of isolation: either can still be opened, and locked off, on its own.", marks: [] },
    ],
    why: "With the interlock, the engine feeds the site or the data centre, never both. Every swap takes the engine off load and back through re-sync, with nothing mining or exporting in between. On one shared busbar the miners simply take whatever the site doesn't use, and our software turns them up and down, so no breaker moves in normal running.",
    done: "Both ACBs can be closed together, and the drawings show them normally closed.",
  },
  { /* 2 Add trip gear to the rack MCCBs */
    needed: [
      { text: "Fit an undervoltage-release (UVR) coil to both 400 A rack MCCBs (Rack 1 and Rack 3), fed through the trip circuit.", marks: ['uvr'] },
      { text: "Fit a motor operator to each, so our controller can close the racks again from a distance once the engine is back.", marks: ['rack-mccbs'] },
      { text: "Fit status contacts to each (open, closed and tripped), wired to our controller's terminals.", marks: ['rack-mccbs'] },
      { text: "Leave the dry cooler and CDU pump breakers without trip gear: the cooling stays on through an engine trip.", marks: ['cool-cdu'] },
    ],
    why: "A UVR coil holds its breaker closed only while the trip circuit keeps it energised. Anything that breaks that circuit (the engine stopping, our controller failing, or a cut wire) opens the racks at once, so the miners can never run on grid power. The motor operators and status contacts let us bring the racks back and see their state without anyone on site.",
    done: "Each rack MCCB opens when its UVR loses supply, reports its state, and closes again on command.",
  },
  { /* 3 Wire the engine-status trip */
    needed: [
      { text: "Take a volt-free \"breaker closed\" contact from the 2G generator breaker: closed while the engine is connected, open when it is not.", marks: ['gen-breaker'] },
      { text: "Run a control cable from that contact in the 2G container to the new board.", marks: ['trip-cable'] },
      { text: "Fit an interposing relay in the new board, held in by that contact.", marks: ['trip-relay'] },
      { text: "Wire the relay into the UVR circuit of both rack MCCBs. When the generator breaker opens, the relay drops out and both racks trip.", marks: ['uvr'] },
    ],
    why: "If the engine stops, the grid becomes the busbar's only source, and the miners would carry on drawing their full load from it. The generator breaker's own contact is the fastest, surest sign the engine has gone: it needs no software and no network, and because the trip works by the circuit opening, a broken wire trips the racks too. The interposing relay keeps 2G's control wiring separate from ours.",
    done: "Opening the generator breaker trips both rack MCCBs in under 0.1 s.",
  },
  { /* 4 Add the controller watchdog */
    needed: [
      { text: "Our controller sends a steady heartbeat out on its terminals in the marshalling section.", marks: ['controller'] },
      { text: "Fit a watchdog relay that stays energised only while that heartbeat keeps arriving.", marks: ['watchdog'] },
      { text: "Wire its contact into the same rack trip circuit as the engine-status relay, so either one opening trips both racks.", marks: ['uvr'] },
    ],
    why: "Our controller is what turns the miners down when power is worth more than mining, and what keeps them off grid power. If it crashes, hangs or loses power, nothing is steering the miners, so its silence has to count as a trip. The watchdog makes a dead controller fail safe.",
    done: "Stopping the heartbeat trips both rack MCCBs.",
  },
  { /* 5 Measure the grid boundary */
    needed: [
      { text: "Clamp split-core CTs, one per phase, around the transformer incomer cables.", marks: ['incomer-cts'] },
      { text: "Wire them to a meter that reads import and export, reporting on Modbus TCP.", marks: ['boundary-meter'] },
      { text: "Do no copper work on the old board: split-core CTs close around the cables, so nothing on the 2014 board is disconnected or changed.", marks: [] },
    ],
    why: "The incomer is where the site meets the grid. Our controller needs to know, second by second, whether the site is importing or exporting there, so it can give the miners exactly the surplus, leave a small export margin, and never pull grid power in to mine.",
    done: "Our controller reads import and export at the incomer over Modbus TCP.",
  },
  { /* 6 Meter the data centre */
    needed: [
      { text: "Fit an MID-approved meter on the data centre feed.", marks: ['dc-meter'] },
      { text: "Move the multifunction meter in LF42344 to the CHP incomer, so it measures what the engine makes.", marks: ['chp-meter'] },
      { text: "Put both meters on Modbus TCP, on the same network as the boundary meter.", marks: ['ethernet'] },
    ],
    why: "The data centre's energy is what gets paid for, so it needs a meter approved for billing, and MID approval is that standard. Metering the engine too means our controller sees the whole balance from three meters it reads directly: what the engine makes, what the data centre uses, and what crosses the boundary.",
    done: "Data centre energy and CHP output both read over Modbus TCP, the data centre from an MID-approved meter.",
  },
  { /* 7 Add a marshalling section */
    needed: [
      { text: "Add a marshalling section to the new board, where all control wiring lands on terminals for our controller.", marks: ['marshalling'] },
      { text: "Fit an Ethernet switch there, networking our controller and the three meters.", marks: ['ethernet'] },
      { text: "Supply it with 230 V taken from the grid side, backed by a UPS.", marks: ['ups'] },
      { text: "Fit a local/remote switch.", marks: ['local-remote'] },
    ],
    why: "One marshalling section gives every control signal (the trips, the watchdog, breaker status, the motor operators and the meters) a single labelled place to connect, test and fault-find, away from the power busbars. Its supply comes from the grid side and rides on a UPS, so our controller stays up when the engine trips, which is exactly when it is needed. The local/remote switch lets an engineer on site take control and block remote commands while they work.",
    done: "Our controller, the switch and the meters stay powered through an engine trip, and Local blocks remote commands.",
  },
  { /* 8 Issue drawings before build */
    needed: [
      { text: "Issue a single-line diagram of the board as it will be built, showing every change on this list.", marks: ['sld'] },
      { text: "Issue a kiosk plan: both boards back to back, the door swings, and the space to withdraw each ACB.", marks: ['kiosk-plan'] },
      { text: "Allow for our review and sign-off before building starts.", marks: [] },
    ],
    why: "Drawings are the cheapest place to catch a mistake. The single-line diagram lets everyone check the scheme before metal is cut: no interlock, the trip circuit, the meters. The kiosk plan proves the two boards fit back to back with their doors open and the ACBs drawn out, one of the checks we make before ordering.",
    done: "We have signed off the single-line diagram and the kiosk plan.",
  },
  { /* 9 Check the parallel case */
    needed: [
      { text: "Work out the fault level on the shared busbar with the grid and the engine both connected.", marks: ['fault'] },
      { text: "Confirm the ACBs, the MCCBs and the busbar are all rated to break and withstand that combined fault level.", marks: ['dc-acb', 'rack-mccbs'] },
      { text: "Check discrimination: for a fault on any outgoing way, the breaker nearest the fault opens first, leaving the ACBs and the generator breaker in.", marks: ['busbar'] },
    ],
    why: "In Lee's design the data centre section is only ever fed by the engine on its own. On a shared busbar a fault there is fed by the grid and the engine together, so more fault current flows than the section was chosen for. The equipment has to survive that safely, and a fault on one rack should only ever take out that rack.",
    done: "A fault-level and discrimination check for the parallel case, with every device rated for it.",
  },
  { /* 10 Prove the trip chain */
    needed: [
      { text: "Open the engine breaker (at FAT, by opening a stand-in for its contact): both rack MCCBs must trip.", marks: ['gen-breaker'] },
      { text: "Then stop our controller's heartbeat: both rack MCCBs must trip again.", marks: ['controller'] },
      { text: "Run both tests at FAT and again at commissioning, recording each trip, with RenewaBlox there to witness them.", marks: ['rack-mccbs'] },
    ],
    why: "These two trips are what keep the data centre off grid power when something goes wrong, so they have to be proven end to end on the real wiring, not taken on trust from the drawings. Testing at the factory catches wiring faults early; testing again on site proves the link to 2G's breaker and to our controller.",
    done: "Both tests pass at FAT and at commissioning, witnessed by RenewaBlox.",
  },
  { /* 11 Price changes line by line */
    needed: [
      { text: "Revise LF42344 with each change on this list priced as its own line.", marks: [] },
      { text: "Say whether an 800 A MCCB can replace the 1250 A data centre ACB, and what it saves.", marks: ['dc-acb'] },
    ],
    why: "Line-by-line prices let us see what each change costs and decide on each one, instead of taking one new total. The data centre feed may not need a 1250 A ACB: an 800 A MCCB could be cheaper and smaller, if it suits the load and the fault level.",
    done: "A revised quote with every change itemised, and an answer on the 800 A MCCB.",
  },
];
