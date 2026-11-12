"use strict";

// Council acceptance is the full four-service mandate flow. Keep one recovery-capable
// implementation so a timeout can never leave a second live organization task behind.
process.env.DONGZHOU_ACCEPTANCE_LABEL ||= "council-current";
process.env.DONGZHOU_TEST_URL ||= "http://127.0.0.1:8780/";

require("./test-live-kernel-mandate-acceptance.js");
