/* AZ Restaurant Partners — trilingual engine (EN / हिंदी / اردو)
   Translations are machine-assisted drafts — have a native speaker review before launch. */
(function () {
  const norm = (s) => s.replace(/\s+/g, ' ').trim();

  // [ english(innerHTML) , hindi , urdu ]
  const ROWS = [
    // NAV
    [`How we work`, `हम कैसे काम करते हैं`, `ہم کیسے کام کرتے ہیں`],
    [`What's possible`, `क्या मुमकिन है`, `کیا ممکن ہے`],
    [`Find your fit`, `अपने लिए सही चुनें`, `اپنے لیے صحیح چنیں`],
    [`Book a free call`, `मुफ़्त कॉल बुक करें`, `مفت کال بُک کریں`],

    // HERO
    [`For the independent, family-run restaurant · Spring &amp; Greater Houston, TX`, `आज़ाद, परिवार-संचालित रेस्तराँ के लिए · स्प्रिंग और ग्रेटर ह्यूस्टन, TX`, `خود مختار، خاندانی ریستوران کے لیے · اسپرنگ اور گریٹر ہیوسٹن، TX`],
    [`You're working harder than ever. <em>So why is someone else keeping the profit?</em>`, `आप पहले से ज़्यादा मेहनत कर रहे हैं। <em>फिर मुनाफ़ा कोई और क्यों रख रहा है?</em>`, `آپ پہلے سے زیادہ محنت کر رہے ہیں۔ <em>پھر منافع کوئی اور کیوں رکھ رہا ہے؟</em>`],
    [`You've given this place your weekends, your sleep, your everything — and still the apps, the fees, and a dozen systems you never asked for take more of the reward than you do. A busy takeout counter, a full dining room, or a few locations — it's the same squeeze: you're working for everyone but yourself. We're a restaurant family who've lived it, and <strong>we don't get paid until you're keeping more</strong>. One free call, and you'll know exactly where your money's been hiding.`, `आपने इस जगह को अपने वीकेंड, अपनी नींद, अपना सब कुछ दिया है — और फिर भी ऐप्स, फ़ीस, और दर्जनों ऐसे सिस्टम जो आपने कभी माँगे ही नहीं, आपसे ज़्यादा फ़ायदा ले जाते हैं। एक व्यस्त टेकआउट काउंटर हो, भरा हुआ डाइनिंग रूम हो, या कुछ लोकेशन — दबाव वही है: आप सबके लिए काम कर रहे हैं, बस अपने लिए नहीं। हम एक रेस्तराँ परिवार हैं जिसने यह सब झेला है, और <strong>जब तक आप ज़्यादा बचाना शुरू न करें, हम पैसे नहीं लेते</strong>। बस एक मुफ़्त कॉल, और आप जान जाएँगे कि आपका पैसा असल में कहाँ छिपा है।`, `آپ نے اس جگہ کو اپنے ویک اینڈ، اپنی نیند، اپنا سب کچھ دیا ہے — اور پھر بھی ایپس، فیس، اور درجنوں ایسے سسٹم جو آپ نے کبھی مانگے ہی نہیں، آپ سے زیادہ فائدہ لے جاتے ہیں۔ ایک مصروف ٹیک آؤٹ کاؤنٹر ہو، بھرا ہوا ڈائننگ روم ہو، یا چند مقامات — دباؤ وہی ہے: آپ سب کے لیے کام کر رہے ہیں، بس اپنے لیے نہیں۔ ہم ایک ریستوران خاندان ہیں جس نے یہ سب جھیلا ہے، اور <strong>جب تک آپ زیادہ بچانا شروع نہ کریں، ہم پیسے نہیں لیتے</strong>۔ بس ایک مفت کال، اور آپ جان جائیں گے کہ آپ کا پیسہ اصل میں کہاں چھپا ہے۔`],
    [`Book your free call`, `अपनी मुफ़्त कॉल बुक करें`, `اپنی مفت کال بُک کریں`],
    [`Find your fit <span aria-hidden="true">→</span>`, `अपने लिए सही चुनें <span aria-hidden="true">→</span>`, `اپنے لیے صحیح چنیں <span aria-hidden="true">→</span>`],
    [`Abbas Zoeb — Founder &amp; Operator`, `अब्बास ज़ोएब — संस्थापक और संचालक`, `عباس ذوئب — بانی و آپریٹر`],

    // CREDS
    [`A restaurant family`, `एक रेस्तराँ परिवार`, `ایک ریستوران خاندان`],
    [`15+ years in hospitality — Canada, India &amp; Texas`, `15+ साल का हॉस्पिटैलिटी अनुभव — कनाडा, भारत और टेक्सस`, `ہاسپٹیلٹی میں 15+ سال — کینیڈا، انڈیا اور ٹیکساس`],
    [`We run our own`, `हमारा अपना रेस्तराँ`, `ہمارا اپنا ریستوران`],
    [`Wok &amp; Karahi, Houston — highly rated &amp; profitable every year`, `Wok &amp; Karahi, ह्यूस्टन — बेहतरीन रेटिंग और हर साल मुनाफ़े में`, `Wok &amp; Karahi، ہیوسٹن — اعلیٰ ریٹنگ اور ہر سال منافع میں`],
    [`Serious tech, on your side`, `मज़बूत टेक, आपके साथ`, `مضبوط ٹیک، آپ کے ساتھ`],
    [`The same engineers big companies rely on — building for your restaurant`, `वही इंजीनियर जिन पर बड़ी कंपनियाँ भरोसा करती हैं — आपके रेस्तराँ के लिए`, `وہی انجینئر جن پر بڑی کمپنیاں بھروسا کرتی ہیں — آپ کے ریستوران کے لیے`],
    [`Only on your side`, `सिर्फ़ आपकी तरफ़`, `صرف آپ کی طرف`],
    [`We take no app or vendor commissions`, `हम किसी ऐप या वेंडर से कमीशन नहीं लेते`, `ہم کسی ایپ یا وینڈر سے کمیشن نہیں لیتے`],

    // BAND
    [`Here's where the money actually goes.`, `पैसा असल में कहाँ जाता है, देखिए।`, `پیسہ اصل میں کہاں جاتا ہے، دیکھیے۔`],
    [`You cook the food — then watch the money walk out the door:`, `आप खाना बनाते हैं — और फिर पैसा दरवाज़े से बाहर जाते देखते हैं:`, `آپ کھانا بناتے ہیں — اور پھر پیسہ دروازے سے باہر جاتے دیکھتے ہیں:`],
    [`The app keeps <strong>15–30%</strong> of the order — some nights more than you make.`, `ऐप ऑर्डर का <strong>15–30%</strong> रख लेता है — कई रातों आपसे भी ज़्यादा।`, `ایپ آرڈر کا <strong>15–30%</strong> رکھ لیتا ہے — کئی راتوں آپ سے بھی زیادہ۔`],
    [`The guest who ordered is <strong>the app's customer, not yours</strong> — you can't even see your own regulars.`, `जिसने ऑर्डर किया वह <strong>ऐप का ग्राहक है, आपका नहीं</strong> — आप अपने नियमित ग्राहक तक नहीं देख पाते।`, `جس نے آرڈر کیا وہ <strong>ایپ کا گاہک ہے، آپ کا نہیں</strong> — آپ اپنے مستقل گاہک تک نہیں دیکھ پاتے۔`],
    [`The phone rings through dinner with <strong>no one free to grab it</strong>.`, `डिनर के बीच फ़ोन बजता रहता है पर <strong>उठाने वाला कोई नहीं</strong>।`, `ڈنر کے دوران فون بجتا رہتا ہے مگر <strong>اٹھانے والا کوئی نہیں</strong>۔`],
    [`Three tablets on the counter, <strong>re-keyed by hand</strong>.`, `काउंटर पर तीन टैबलेट, <strong>हाथ से दोबारा टाइप करते</strong>।`, `کاؤنٹر پر تین ٹیبلٹ، <strong>ہاتھ سے دوبارہ ٹائپ کرتے</strong>۔`],
    [`<em>None of it is permanent.</em> The apps are great for getting you <em>discovered</em> — the trick is not letting them keep the customer. We've done exactly this on our own restaurant, and we'll do it for yours: turn app guests into your own regulars, connect the right tools, and keep what you earn — and from the <strong>100+ tools out there</strong>, we bring you only the few that actually fit.`, `<em>यह सब हमेशा के लिए नहीं है।</em> ऐप्स आपको <em>नए लोगों तक पहुँचाने</em> में अच्छे हैं — असली बात है उन्हें ग्राहक रखने न देना। हमने यही अपने रेस्तराँ पर किया है, और आपके लिए भी करेंगे: ऐप के ग्राहकों को अपने नियमित ग्राहक बनाएँ, सही टूल जोड़ें, और अपनी कमाई अपने पास रखें — और <strong>100+ टूल्स में से</strong> हम सिर्फ़ वही चुनिंदा लाते हैं जो आप पर सही बैठें।`, `<em>یہ سب ہمیشہ کے لیے نہیں ہے۔</em> ایپس آپ کو <em>نئے لوگوں تک پہنچانے</em> میں اچھے ہیں — اصل بات ہے انہیں گاہک رکھنے نہ دینا۔ ہم نے یہی اپنے ریستوران پر کیا ہے، اور آپ کے لیے بھی کریں گے: ایپ کے گاہکوں کو اپنے مستقل گاہک بنائیں، صحیح ٹولز جوڑیں، اور اپنی کمائی اپنے پاس رکھیں — اور <strong>100+ ٹولز میں سے</strong> ہم صرف وہی چند لاتے ہیں جو آپ پر صحیح بیٹھیں۔`],

    // STATS
    [`of US restaurants didn't turn a profit last year <em>(National Restaurant Association)</em>.`, `अमेरिकी रेस्तराँ पिछले साल मुनाफ़ा नहीं कमा पाए <em>(National Restaurant Association)</em>।`, `امریکی ریستوران پچھلے سال منافع نہیں کما سکے <em>(National Restaurant Association)</em>۔`],
    [`what it costs to take an order on your own site — versus up to 30% the delivery apps keep.`, `अपनी साइट पर ऑर्डर लेने का खर्च — जबकि डिलीवरी ऐप्स 30% तक रख लेते हैं।`, `اپنی سائٹ پر آرڈر لینے کا خرچ — جبکہ ڈیلیوری ایپس 30% تک رکھ لیتے ہیں۔`],
    [`more revenue for an independent with each one-star rating bump <em>(Harvard Business School)</em>.`, `हर एक-स्टार रेटिंग बढ़ने पर एक आज़ाद रेस्तराँ की ज़्यादा कमाई <em>(Harvard Business School)</em>।`, `ہر ایک-اسٹار ریٹنگ بڑھنے پر ایک خود مختار ریستوران کی زیادہ آمدنی <em>(Harvard Business School)</em>۔`],
    [`only 28% of operators say tech ever improved their profit — we're built to be the exception <em>(National Restaurant Association)</em>.`, `सिर्फ़ 28% मालिक कहते हैं कि टेक से उनका मुनाफ़ा बढ़ा — हम अपवाद बनने के लिए बने हैं <em>(National Restaurant Association)</em>।`, `صرف 28% مالکان کہتے ہیں کہ ٹیک سے ان کا منافع بڑھا — ہم استثنا بننے کے لیے بنے ہیں <em>(National Restaurant Association)</em>۔`],

    // MID CTA
    [`See exactly where your restaurant is leaking — free, and yours to keep.`, `देखिए आपका रेस्तराँ कहाँ-कहाँ पैसा खो रहा है — मुफ़्त, और पूरी तरह आपका।`, `دیکھیے آپ کا ریستوران کہاں کہاں پیسہ کھو رہا ہے — مفت، اور پوری طرح آپ کا۔`],

    // HOW WE WORK
    [`One team, end to end — and we never really leave.`, `एक टीम, शुरू से आख़िर तक — और हम कभी सच में नहीं जाते।`, `ایک ٹیم، شروع سے آخر تک — اور ہم کبھی واقعی نہیں جاتے۔`],
    [`You get one person who knows your restaurant, and a full team behind them doing the work. We take you the whole way — from the first leak to the long run.`, `आपको एक व्यक्ति मिलता है जो आपके रेस्तराँ को समझता है, और उसके पीछे काम करती पूरी टीम। हम आपको पूरे रास्ते साथ ले चलते हैं — पहली कमी से लेकर लंबी दौड़ तक।`, `آپ کو ایک شخص ملتا ہے جو آپ کے ریستوران کو سمجھتا ہے، اور اس کے پیچھے کام کرتی پوری ٹیم۔ ہم آپ کو پورے راستے ساتھ لے چلتے ہیں — پہلی کمی سے لے کر لمبی دوڑ تک۔`],
    [`Find the leaks`, `कमियाँ खोजें`, `کمیاں تلاش کریں`],
    [`We dig into your numbers and show you exactly where money's slipping out — then hand you a plan with the cost and the expected return in plain dollars, before you spend a thing.`, `हम आपके आँकड़ों में गहराई से देखते हैं और बताते हैं कि पैसा कहाँ निकल रहा है — फिर खर्च और अनुमानित फ़ायदा साफ़ डॉलर में बताते हुए एक योजना देते हैं, इससे पहले कि आप कुछ खर्च करें।`, `ہم آپ کے اعداد و شمار میں گہرائی سے دیکھتے ہیں اور بتاتے ہیں کہ پیسہ کہاں نکل رہا ہے — پھر خرچ اور متوقع فائدہ صاف ڈالر میں بتاتے ہوئے ایک منصوبہ دیتے ہیں، اس سے پہلے کہ آپ کچھ خرچ کریں۔`],
    [`Stop the bleed, then grow`, `रिसाव रोकें, फिर बढ़ें`, `رساؤ روکیں، پھر بڑھیں`],
    [`We start with the fastest-payback fixes so the work pays for itself — then connect your systems and add the advantages the big chains have, as each one earns its place.`, `हम सबसे जल्दी फ़ायदा देने वाले सुधारों से शुरू करते हैं ताकि काम अपना खर्च खुद निकाल ले — फिर आपके सिस्टम जोड़ते हैं और बड़ी चेन वाली सुविधाएँ जोड़ते हैं, जैसे-जैसे हर एक अपनी जगह बनाए।`, `ہم سب سے جلدی فائدہ دینے والے کاموں سے شروع کرتے ہیں تاکہ کام اپنا خرچ خود نکال لے — پھر آپ کے سسٹم جوڑتے ہیں اور بڑی چین والی سہولتیں شامل کرتے ہیں، جیسے جیسے ہر ایک اپنی جگہ بنائے۔`],
    [`Stay as your team`, `आपकी टीम बनकर रहें`, `آپ کی ٹیم بن کر رہیں`],
    [`We don't hand off and disappear. We stay on as the tech team you could never hire on your own — because it never stops evolving, and neither do we.`, `हम काम सौंपकर ग़ायब नहीं होते। हम वही टेक टीम बनकर रहते हैं जिसे आप अकेले कभी रख नहीं सकते — क्योंकि तकनीक बदलती रहती है, और हम भी।`, `ہم کام سونپ کر غائب نہیں ہوتے۔ ہم وہی ٹیک ٹیم بن کر رہتے ہیں جسے آپ اکیلے کبھی رکھ نہیں سکتے — کیونکہ ٹیکنالوجی بدلتی رہتی ہے، اور ہم بھی۔`],
    [`Our goal isn't to sell you software and walk away. It's to be the team that keeps <strong>your restaurant winning</strong> — this year, and every year after.`, `हमारा मक़सद आपको सॉफ़्टवेयर बेचकर चले जाना नहीं है। हमारा मक़सद वह टीम बनना है जो <strong>आपके रेस्तराँ को जिताती रहे</strong> — इस साल, और हर आने वाले साल।`, `ہمارا مقصد آپ کو سافٹ ویئر بیچ کر چلے جانا نہیں ہے۔ ہمارا مقصد وہ ٹیم بننا ہے جو <strong>آپ کے ریستوران کو جِتاتی رہے</strong> — اس سال، اور ہر آنے والے سال۔`],

    // STORY
    [`Why us`, `हम ही क्यों`, `ہم ہی کیوں`],
    [`We've stood on your side of the line.`, `हम भी उसी तरफ़ खड़े रहे हैं जहाँ आप हैं।`, `ہم بھی اُسی طرف کھڑے رہے ہیں جہاں آپ ہیں۔`],
    [`We're a restaurant family first. <strong>Fifteen-plus years</strong> in hospitality across <strong>Canada and India</strong>, a restaurant of our own in Canada, and today <strong>Wok &amp; Karahi</strong> in Spring, Texas — recognized as the <strong>Best Halal Chinese Indo-Pak in Houston</strong>, and highly rated. We've lived the 12-hour days, the app fees, the no-shows, and the tools that fight you instead of helping.`, `हम सबसे पहले एक रेस्तराँ परिवार हैं। <strong>पंद्रह से ज़्यादा साल</strong> का हॉस्पिटैलिटी अनुभव <strong>कनाडा और भारत</strong> में, कनाडा में अपना एक रेस्तराँ, और आज स्प्रिंग, टेक्सस में <strong>Wok &amp; Karahi</strong> — <strong>ह्यूस्टन का बेस्ट हलाल चाइनीज़ इंडो-पाक</strong> माना गया, और बेहतरीन रेटिंग वाला। हमने भी 12-12 घंटे की मेहनत, ऐप की फ़ीस, न आने वाले ग्राहक, और मदद के बजाय अड़चन बनने वाले टूल झेले हैं।`, `ہم سب سے پہلے ایک ریستوران خاندان ہیں۔ <strong>پندرہ سے زیادہ سال</strong> کا ہاسپٹیلٹی تجربہ <strong>کینیڈا اور انڈیا</strong> میں، کینیڈا میں اپنا ایک ریستوران، اور آج اسپرنگ، ٹیکساس میں <strong>Wok &amp; Karahi</strong> — <strong>ہیوسٹن کا بہترین حلال چائنیز اِنڈو-پاک</strong> مانا گیا، اور اعلیٰ ریٹنگ والا۔ ہم نے بھی 12-12 گھنٹے کی محنت، ایپ کی فیس، نہ آنے والے گاہک، اور مدد کے بجائے رکاوٹ بننے والے ٹولز جھیلے ہیں۔`],
    [`Behind the scenes, we pair that with <strong>serious engineering muscle</strong> — led by our founder, a senior software architect who builds production-grade systems for global companies and works with the newest AI every day. So you get the seven-day-a-week reality of the floor <em>and</em> enterprise-grade capability, in one partner. You deal with one person who genuinely gets it; our team makes it all happen.`, `पर्दे के पीछे, हम इसके साथ जोड़ते हैं <strong>मज़बूत इंजीनियरिंग ताक़त</strong> — हमारे संस्थापक की अगुवाई में, जो एक सीनियर सॉफ़्टवेयर आर्किटेक्ट हैं और दुनिया भर की कंपनियों के लिए प्रोडक्शन-स्तर के सिस्टम बनाते हैं और हर दिन नई से नई AI के साथ काम करते हैं। तो आपको मिलती है फ़्लोर की सातों दिन की हक़ीक़त <em>और</em> एंटरप्राइज़-स्तर की क्षमता, एक ही पार्टनर में। आप एक ऐसे व्यक्ति से बात करते हैं जो सच में समझता है; बाक़ी सब हमारी टीम कर देती है।`, `پردے کے پیچھے، ہم اس کے ساتھ جوڑتے ہیں <strong>مضبوط انجینئرنگ طاقت</strong> — ہمارے بانی کی قیادت میں، جو ایک سینئر سافٹ ویئر آرکیٹیکٹ ہیں اور دنیا بھر کی کمپنیوں کے لیے پروڈکشن-سطح کے سسٹم بناتے ہیں اور ہر دن نئی سے نئی AI کے ساتھ کام کرتے ہیں۔ تو آپ کو ملتی ہے فلور کی ساتوں دن کی حقیقت <em>اور</em> انٹرپرائز-سطح کی صلاحیت، ایک ہی پارٹنر میں۔ آپ ایک ایسے شخص سے بات کرتے ہیں جو واقعی سمجھتا ہے؛ باقی سب ہماری ٹیم کر دیتی ہے۔`],
    [`<strong>A real result:</strong> we doubled a restaurant's online ratings and lifted its score — and for an independent, each star is worth roughly 5–9% in revenue. That's the kind of change we build, not just advise on.`, `<strong>एक असली नतीजा:</strong> हमने एक रेस्तराँ की ऑनलाइन रेटिंग्स की संख्या दोगुनी की और उसका स्कोर बढ़ाया — और एक आज़ाद रेस्तराँ के लिए, हर स्टार करीब 5–9% कमाई के बराबर है। हम ऐसा ही बदलाव बनाते हैं, सिर्फ़ सलाह नहीं देते।`, `<strong>ایک حقیقی نتیجہ:</strong> ہم نے ایک ریستوران کی آن لائن ریٹنگز کی تعداد دوگنی کی اور اس کا اسکور بڑھایا — اور ایک خود مختار ریستوران کے لیے، ہر اسٹار تقریباً 5–9% آمدنی کے برابر ہے۔ ہم ایسا ہی بدلاؤ بناتے ہیں، صرف مشورہ نہیں دیتے۔`],
    [`Abbas &amp; his father, Zoeb — at Wok &amp; Karahi, Spring, TX`, `अब्बास और उनके पिता, ज़ोएब — Wok &amp; Karahi, स्प्रिंग, TX में`, `عباس اور اُن کے والد، ذوئب — Wok &amp; Karahi، اسپرنگ، TX میں`],
    [`Your customers and your data stay yours. We give you the muscle the big chains have — and you keep the keys.`, `आपके ग्राहक और आपका डेटा आपके ही रहते हैं। हम आपको बड़ी चेन वाली ताक़त देते हैं — और चाबियाँ आपके पास रहती हैं।`, `آپ کے گاہک اور آپ کا ڈیٹا آپ ہی کے رہتے ہیں۔ ہم آپ کو بڑی چین والی طاقت دیتے ہیں — اور چابیاں آپ کے پاس رہتی ہیں۔`],
    [`— What AZ Restaurant Partners stands for`, `— AZ Restaurant Partners किसके लिए खड़ा है`, `— AZ Restaurant Partners کس کے لیے کھڑا ہے`],

    // STRATEGIES
    [`How we'd grow your restaurant`, `हम आपका रेस्तराँ कैसे बढ़ाएँगे`, `ہم آپ کا ریستوران کیسے بڑھائیں گے`],
    [`Use what works. Fix what leaks. Own what's yours.`, `जो काम करे उसे अपनाएँ। जो रिसे उसे ठीक करें। जो आपका है उस पर हक़ रखें।`, `جو کام کرے اسے اپنائیں۔ جو رِسے اسے ٹھیک کریں۔ جو آپ کا ہے اس پر حق رکھیں۔`],
    [`We don't fight the apps or rip out what's working — we use them smarter. Tell us what you run, and we'll show you exactly where we'd start:`, `हम ऐप्स से नहीं लड़ते और जो चल रहा है उसे नहीं उखाड़ते — हम उन्हें समझदारी से इस्तेमाल करते हैं। बताइए आप क्या चलाते हैं, और हम बताएँगे कि हम कहाँ से शुरू करेंगे:`, `ہم ایپس سے نہیں لڑتے اور جو چل رہا ہے اسے نہیں اکھاڑتے — ہم انہیں سمجھداری سے استعمال کرتے ہیں۔ بتائیے آپ کیا چلاتے ہیں، اور ہم بتائیں گے کہ ہم کہاں سے شروع کریں گے:`],
    [`Which sounds like you?`, `इनमें से आप कौन हैं?`, `ان میں سے آپ کون ہیں؟`],
    [`Takeout or counter`, `टेकआउट या काउंटर`, `ٹیک آؤٹ یا کاؤنٹر`],
    [`Sit-down restaurant`, `बैठकर खाने वाला रेस्तराँ`, `بیٹھ کر کھانے والا ریستوران`],
    [`2–10 locations`, `2–10 लोकेशन`, `2–10 مقامات`],
    // cards
    [`Treat the apps as discovery — then win the customer`, `ऐप्स को पहचान का ज़रिया मानें — फिर ग्राहक जीतें`, `ایپس کو پہچان کا ذریعہ مانیں — پھر گاہک جیتیں`],
    [`The apps are great at getting you <em>found</em>. The mistake is letting them keep the guest. We capture the customers they send you and turn them into direct, repeat orders on your own site — you keep the relationship and the margin. (Still want to deliver? White-label drivers, ~$8 flat.)`, `ऐप्स आपको <em>ढूँढवाने</em> में बढ़िया हैं। ग़लती है उन्हें ग्राहक रखने देना। हम उनके भेजे ग्राहकों को पकड़ते हैं और उन्हें आपकी अपनी साइट पर सीधे, बार-बार के ऑर्डर में बदलते हैं — रिश्ता और मुनाफ़ा आपके पास। (डिलीवरी भी करनी है? व्हाइट-लेबल ड्राइवर, करीब $8 फ़्लैट।)`, `ایپس آپ کو <em>ڈھونڈوانے</em> میں بہترین ہیں۔ غلطی ہے انہیں گاہک رکھنے دینا۔ ہم ان کے بھیجے گاہکوں کو پکڑتے ہیں اور انہیں آپ کی اپنی سائٹ پر براہِ راست، بار بار کے آرڈر میں بدلتے ہیں — رشتہ اور منافع آپ کے پاس۔ (ڈیلیوری بھی کرنی ہے؟ وائٹ-لیبل ڈرائیور، تقریباً $8 فلیٹ۔)`],
    [`Know your regulars — and bring them back`, `अपने नियमित ग्राहक जानें — और उन्हें वापस लाएँ`, `اپنے مستقل گاہک جانیں — اور انہیں واپس لائیں`],
    [`Right now the apps know your customers and you don't. We help you build your own guest list and quietly bring people back with the right nudge — not blanket discounts — so repeat visits grow on their own.`, `अभी ऐप्स आपके ग्राहकों को जानते हैं, आप नहीं। हम आपकी अपनी ग्राहक सूची बनाने में मदद करते हैं और सही याद-दहानी से लोगों को चुपचाप वापस लाते हैं — हर किसी को छूट देकर नहीं — ताकि बार-बार आने वाले ग्राहक खुद बढ़ें।`, `ابھی ایپس آپ کے گاہکوں کو جانتے ہیں، آپ نہیں۔ ہم آپ کی اپنی گاہک فہرست بنانے میں مدد کرتے ہیں اور صحیح یاد دہانی سے لوگوں کو خاموشی سے واپس لاتے ہیں — ہر کسی کو رعایت دے کر نہیں — تاکہ بار بار آنے والے گاہک خود بڑھیں۔`],
    [`Answer every call, around the clock`, `हर कॉल का जवाब, दिन-रात`, `ہر کال کا جواب، دن رات`],
    [`An AI voice agent takes orders and books tables 24/7, so no rush ever sends money to voicemail.`, `एक AI वॉइस एजेंट 24/7 ऑर्डर लेता है और टेबल बुक करता है, ताकि भीड़ के समय भी कोई पैसा वॉइसमेल में न जाए।`, `ایک AI وائس ایجنٹ 24/7 آرڈر لیتا ہے اور ٹیبل بُک کرتا ہے، تاکہ رش کے وقت بھی کوئی پیسہ وائس میل میں نہ جائے۔`],
    [`End the tablet chaos`, `टैबलेट की अफ़रा-तफ़री ख़त्म करें`, `ٹیبلٹ کی افراتفری ختم کریں`],
    [`All your delivery apps flowing into one screen and into your POS — instead of three tablets beeping at the counter and orders re-keyed by hand.`, `आपके सारे डिलीवरी ऐप्स एक ही स्क्रीन और आपके POS में आते हुए — काउंटर पर तीन टैबलेट बजने और हाथ से ऑर्डर दोबारा टाइप करने के बजाय।`, `آپ کے سارے ڈیلیوری ایپس ایک ہی اسکرین اور آپ کے POS میں آتے ہوئے — کاؤنٹر پر تین ٹیبلٹ بجنے اور ہاتھ سے آرڈر دوبارہ ٹائپ کرنے کے بجائے۔`],
    [`More 5-star reviews — the smart way`, `ज़्यादा 5-स्टार रिव्यू — समझदारी से`, `زیادہ 5-اسٹار ریویوز — سمجھداری سے`],
    [`We nudge happy guests to post publicly and catch unhappy ones privately before they do — so your rating climbs steadily and every review gets answered on time. For an independent, each star is worth roughly 5–9% in revenue.`, `हम ख़ुश ग्राहकों को सार्वजनिक रिव्यू के लिए प्रेरित करते हैं और नाख़ुश ग्राहकों को पहले ही निजी तौर पर पकड़ लेते हैं — ताकि आपकी रेटिंग लगातार बढ़े और हर रिव्यू का समय पर जवाब हो। एक आज़ाद रेस्तराँ के लिए, हर स्टार करीब 5–9% कमाई के बराबर है।`, `ہم خوش گاہکوں کو عوامی ریویو کے لیے ابھارتے ہیں اور ناخوش گاہکوں کو پہلے ہی نجی طور پر پکڑ لیتے ہیں — تاکہ آپ کی ریٹنگ مسلسل بڑھے اور ہر ریویو کا بروقت جواب ہو۔ ایک خود مختار ریستوران کے لیے، ہر اسٹار تقریباً 5–9% آمدنی کے برابر ہے۔`],
    [`Get found by AI, not just Google`, `सिर्फ़ Google नहीं, AI पर भी मिलें`, `صرف Google نہیں، AI پر بھی ملیں`],
    [`Make your menu and hours readable to ChatGPT, Gemini, and Maps, so you're the place they recommend — and the orders follow.`, `अपना मेन्यू और समय ChatGPT, Gemini और Maps के पढ़ने लायक बनाएँ, ताकि वे आपको ही सुझाएँ — और ऑर्डर पीछे-पीछे आएँ।`, `اپنا مینو اور اوقات ChatGPT، Gemini اور Maps کے پڑھنے لائق بنائیں، تاکہ وہ آپ ہی کو تجویز کریں — اور آرڈر پیچھے پیچھے آئیں۔`],
    [`Catering &amp; corporate lunches, done right`, `कैटरिंग और कॉर्पोरेट लंच, सही तरीक़े से`, `کیٹرنگ اور کارپوریٹ لنچ، صحیح طریقے سے`],
    [`A real catering channel — bigger orders, recurring office lunches, white-label delivery — at margins far above your dine-in.`, `एक असली कैटरिंग चैनल — बड़े ऑर्डर, नियमित ऑफ़िस लंच, व्हाइट-लेबल डिलीवरी — आपके डाइन-इन से कहीं ज़्यादा मुनाफ़े पर।`, `ایک حقیقی کیٹرنگ چینل — بڑے آرڈر، باقاعدہ آفس لنچ، وائٹ-لیبل ڈیلیوری — آپ کے ڈائن-اِن سے کہیں زیادہ منافع پر۔`],
    [`Recover what the apps owe you`, `जो ऐप्स पर बकाया है वह वसूलें`, `جو ایپس پر واجب ہے وہ وصول کریں`],
    [`The apps quietly short you — wrong charges, bogus refunds, missed payouts. We audit them and claw back the money that's actually yours, then keep watching so it doesn't pile up again.`, `ऐप्स चुपचाप आपका हक़ मारते हैं — ग़लत चार्ज, झूठे रिफ़ंड, छूटे भुगतान। हम उनकी जाँच करते हैं और वह पैसा वापस खींचते हैं जो असल में आपका है, फिर नज़र रखते हैं ताकि दोबारा न जमा हो।`, `ایپس خاموشی سے آپ کا حق مارتے ہیں — غلط چارجز، جھوٹے ریفنڈ، چھوٹی ادائیگیاں۔ ہم ان کا آڈٹ کرتے ہیں اور وہ پیسہ واپس کھینچتے ہیں جو اصل میں آپ کا ہے، پھر نظر رکھتے ہیں تاکہ دوبارہ جمع نہ ہو۔`],
    // fit lines
    [`<span class="yes">Fit if</span> the apps bring orders but you never see the customer again.`, `<span class="yes">सही अगर</span> ऐप्स ऑर्डर तो लाते हैं पर ग्राहक दोबारा कभी नहीं दिखता।`, `<span class="yes">صحیح اگر</span> ایپس آرڈر تو لاتے ہیں مگر گاہک دوبارہ کبھی نہیں دکھتا۔`],
    [`<span class="no">Maybe not</span> if you do little delivery or takeout.`, `<span class="no">शायद नहीं</span> अगर आप बहुत कम डिलीवरी या टेकआउट करते हैं।`, `<span class="no">شاید نہیں</span> اگر آپ بہت کم ڈیلیوری یا ٹیک آؤٹ کرتے ہیں۔`],
    [`<span class="yes">Fit if</span> you couldn't email your top 20 regulars today.`, `<span class="yes">सही अगर</span> आप आज अपने टॉप 20 नियमित ग्राहकों को ईमेल नहीं कर सकते।`, `<span class="yes">صحیح اگر</span> آپ آج اپنے ٹاپ 20 مستقل گاہکوں کو ای میل نہیں کر سکتے۔`],
    [`<span class="no">Maybe not</span> if you already run a healthy first-party list.`, `<span class="no">शायद नहीं</span> अगर आपके पास पहले से अच्छी ग्राहक सूची है।`, `<span class="no">شاید نہیں</span> اگر آپ کے پاس پہلے سے اچھی گاہک فہرست ہے۔`],
    [`<span class="yes">Fit if</span> you lose takeout or reservation calls during peaks.`, `<span class="yes">सही अगर</span> भीड़ के समय आपके टेकआउट या रिज़र्वेशन कॉल छूट जाते हैं।`, `<span class="yes">صحیح اگر</span> رش کے وقت آپ کے ٹیک آؤٹ یا ریزرویشن کالز چھوٹ جاتے ہیں۔`],
    [`<span class="no">Maybe not</span> if your call volume is genuinely low.`, `<span class="no">शायद नहीं</span> अगर आपके यहाँ कॉल वाक़ई बहुत कम आते हैं।`, `<span class="no">شاید نہیں</span> اگر آپ کے یہاں کالز واقعی بہت کم آتے ہیں۔`],
    [`<span class="yes">Fit if</span> you're juggling DoorDash, Uber &amp; Grubhub tablets.`, `<span class="yes">सही अगर</span> आप DoorDash, Uber और Grubhub के टैबलेट संभाल रहे हैं।`, `<span class="yes">صحیح اگر</span> آپ DoorDash، Uber اور Grubhub کے ٹیبلٹ سنبھال رہے ہیں۔`],
    [`<span class="no">Maybe not</span> if the apps already feed your POS.`, `<span class="no">शायद नहीं</span> अगर ऐप्स पहले से आपके POS में आते हैं।`, `<span class="no">شاید نہیں</span> اگر ایپس پہلے سے آپ کے POS میں آتے ہیں۔`],
    [`<span class="yes">Fit if</span> your rating is stuck or slipping.`, `<span class="yes">सही अगर</span> आपकी रेटिंग अटकी है या गिर रही है।`, `<span class="yes">صحیح اگر</span> آپ کی ریٹنگ اٹکی ہے یا گر رہی ہے۔`],
    [`<span class="no">Maybe not</span> as a top priority for big chains.`, `<span class="no">शायद नहीं</span> बड़ी चेन के लिए सबसे पहली प्राथमिकता के तौर पर।`, `<span class="no">شاید نہیں</span> بڑی چین کے لیے سب سے پہلی ترجیح کے طور پر۔`],
    [`<span class="yes">Fit if</span> people search "best [your food] near me."`, `<span class="yes">सही अगर</span> लोग "best [आपका खाना] near me" सर्च करते हैं।`, `<span class="yes">صحیح اگر</span> لوگ "best [آپ کا کھانا] near me" سرچ کرتے ہیں۔`],
    [`<span class="no">Maybe not</span> if you're purely a regulars-only neighborhood spot.`, `<span class="no">शायद नहीं</span> अगर आप सिर्फ़ मोहल्ले के नियमित ग्राहकों वाली जगह हैं।`, `<span class="no">شاید نہیں</span> اگر آپ صرف محلے کے مستقل گاہکوں والی جگہ ہیں۔`],
    [`<span class="yes">Fit if</span> you've got kitchen capacity and local offices nearby.`, `<span class="yes">सही अगर</span> आपके पास किचन की गुंजाइश है और आस-पास ऑफ़िस हैं।`, `<span class="yes">صحیح اگر</span> آپ کے پاس کچن کی گنجائش ہے اور آس پاس آفس ہیں۔`],
    [`<span class="no">Maybe not</span> if you're already at full capacity at peak.`, `<span class="no">शायद नहीं</span> अगर आप भीड़ के समय पहले से पूरी क्षमता पर हैं।`, `<span class="no">شاید نہیں</span> اگر آپ رش کے وقت پہلے سے پوری گنجائش پر ہیں۔`],
    [`<span class="yes">Fit if</span> you run real delivery volume across the apps.`, `<span class="yes">सही अगर</span> आप ऐप्स पर अच्छी-ख़ासी डिलीवरी करते हैं।`, `<span class="yes">صحیح اگر</span> آپ ایپس پر خاصی ڈیلیوری کرتے ہیں۔`],
    [`<span class="no">Maybe not</span> if delivery is a tiny part of your business.`, `<span class="no">शायद नहीं</span> अगर डिलीवरी आपके कारोबार का बहुत छोटा हिस्सा है।`, `<span class="no">شاید نہیں</span> اگر ڈیلیوری آپ کے کاروبار کا بہت چھوٹا حصہ ہے۔`],
    [`See all plays`, `सभी तरीक़े देखें`, `تمام طریقے دیکھیں`],
    [`These are the high-impact plays — but there are <strong>100+ tools</strong> out there, and most owners don't know which (if any) fit them. <a href="#finder">See what fits your restaurant →</a>`, `ये सबसे असरदार तरीक़े हैं — पर बाहर <strong>100+ टूल्स</strong> मौजूद हैं, और ज़्यादातर मालिकों को पता ही नहीं कि कौन-सा (अगर कोई) उन पर सही बैठता है। <a href="#finder">देखें आपके रेस्तराँ पर क्या सही बैठता है →</a>`, `یہ سب سے مؤثر طریقے ہیں — مگر باہر <strong>100+ ٹولز</strong> موجود ہیں، اور زیادہ تر مالکان کو پتا ہی نہیں کہ کون سا (اگر کوئی) ان پر صحیح بیٹھتا ہے۔ <a href="#finder">دیکھیں آپ کے ریستوران پر کیا صحیح بیٹھتا ہے →</a>`],

    // FINDER
    [`What's out there — and what fits you`, `बाहर क्या-क्या है — और आप पर क्या सही बैठता है`, `باہر کیا کیا ہے — اور آپ پر کیا صحیح بیٹھتا ہے`],
    [`There's a tool for everything. You only need the right few.`, `हर चीज़ के लिए एक टूल है। आपको बस सही चंद चाहिए।`, `ہر چیز کے لیے ایک ٹول ہے۔ آپ کو بس صحیح چند چاہئیں۔`],
    [`We track <strong>100+ restaurant tools across 22 categories</strong> — and most owners have never heard of the handful that would actually move their numbers. Tap the <span class="finder__hintword">highlighted words</span> to describe your place, and we'll show you what likely fits, what it tends to cost, and what to skip — then send the full breakdown and set up your free call.`, `हम <strong>22 श्रेणियों में 100+ रेस्तराँ टूल्स</strong> पर नज़र रखते हैं — और ज़्यादातर मालिकों ने उन चंद टूल्स का नाम तक नहीं सुना जो वाक़ई उनके आँकड़े बदल देंगे। अपनी जगह बताने के लिए <span class="finder__hintword">हाइलाइट किए शब्दों</span> पर टैप करें, और हम बताएँगे कि क्या सही बैठेगा, उसका आम तौर पर क्या खर्च होता है, और क्या छोड़ देना है — फिर पूरा ब्यौरा भेजेंगे और आपकी मुफ़्त कॉल तय करेंगे।`, `ہم <strong>22 زمروں میں 100+ ریستوران ٹولز</strong> پر نظر رکھتے ہیں — اور زیادہ تر مالکان نے ان چند ٹولز کا نام تک نہیں سنا جو واقعی ان کے اعداد بدل دیں گے۔ اپنی جگہ بتانے کے لیے <span class="finder__hintword">نمایاں کیے گئے الفاظ</span> پر ٹیپ کریں، اور ہم بتائیں گے کہ کیا صحیح بیٹھے گا، اس کا عام طور پر کیا خرچ ہوتا ہے، اور کیا چھوڑ دینا ہے — پھر پورا تفصیلی خاکہ بھیجیں گے اور آپ کی مفت کال طے کریں گے۔`],

    // FAQ
    [`Good questions`, `अच्छे सवाल`, `اچھے سوالات`],
    [`What owners ask us first.`, `मालिक हमसे सबसे पहले क्या पूछते हैं।`, `مالکان ہم سے سب سے پہلے کیا پوچھتے ہیں۔`],
    [`Is this just one person?`, `क्या यह सिर्फ़ एक आदमी है?`, `کیا یہ صرف ایک آدمی ہے؟`],
    [`No. You get <em>one</em> point of contact who knows your restaurant — and a full team behind them building, integrating, testing, and running everything to a production-grade standard. One relationship, real horsepower.`, `नहीं। आपको <em>एक</em> संपर्क व्यक्ति मिलता है जो आपके रेस्तराँ को जानता है — और उसके पीछे पूरी टीम जो सब कुछ बनाती, जोड़ती, जाँचती और प्रोडक्शन-स्तर पर चलाती है। एक रिश्ता, असली ताक़त।`, `نہیں۔ آپ کو <em>ایک</em> رابطہ شخص ملتا ہے جو آپ کے ریستوران کو جانتا ہے — اور اس کے پیچھے پوری ٹیم جو سب کچھ بناتی، جوڑتی، جانچتی اور پروڈکشن-سطح پر چلاتی ہے۔ ایک رشتہ، حقیقی طاقت۔`],
    [`What happens on the free call?`, `मुफ़्त कॉल पर क्या होता है?`, `مفت کال پر کیا ہوتا ہے؟`],
    [`We talk through your restaurant — where it's winning and where it's leaking money — and point you to the highest-impact move, whether or not we end up working together. No slides, no pressure.`, `हम आपके रेस्तराँ पर बात करते हैं — कहाँ अच्छा चल रहा है और कहाँ पैसा रिस रहा है — और सबसे असरदार क़दम बताते हैं, चाहे हम साथ काम करें या नहीं। न स्लाइड्स, न दबाव।`, `ہم آپ کے ریستوران پر بات کرتے ہیں — کہاں اچھا چل رہا ہے اور کہاں پیسہ رِس رہا ہے — اور سب سے مؤثر قدم بتاتے ہیں، چاہے ہم ساتھ کام کریں یا نہیں۔ نہ سلائیڈز، نہ دباؤ۔`],
    [`Do you disappear after it's built?`, `बनाने के बाद क्या आप ग़ायब हो जाते हैं?`, `بنانے کے بعد کیا آپ غائب ہو جاتے ہیں؟`],
    [`Never. We don't do drop-and-leave. We stay on — automated monitoring plus real check-ins — because the tools and the market keep evolving, and so should your restaurant. That long-term partnership is the whole point.`, `कभी नहीं। हम बनाकर छोड़ने वाले नहीं हैं। हम साथ रहते हैं — ऑटोमेटेड निगरानी और असली बातचीत — क्योंकि टूल और बाज़ार बदलते रहते हैं, और आपके रेस्तराँ को भी बदलना चाहिए। यही लंबी साझेदारी असल मक़सद है।`, `کبھی نہیں۔ ہم بنا کر چھوڑنے والے نہیں ہیں۔ ہم ساتھ رہتے ہیں — خودکار نگرانی اور حقیقی رابطے — کیونکہ ٹولز اور مارکیٹ بدلتے رہتے ہیں، اور آپ کے ریستوران کو بھی بدلنا چاہیے۔ یہی طویل شراکت اصل مقصد ہے۔`],
    [`Can't I just do this myself?`, `क्या मैं यह ख़ुद नहीं कर सकता?`, `کیا میں یہ خود نہیں کر سکتا؟`],
    [`You can — and the finder above points you straight to the tools. But choosing among dozens of options, wiring them into your POS, and proving the ROI is the hard, time-consuming part. That's exactly what we do, end to end — so you get the result without the risk.`, `कर सकते हैं — और ऊपर का फ़ाइंडर आपको सीधे टूल्स तक ले जाता है। पर दर्जनों विकल्पों में से चुनना, उन्हें अपने POS से जोड़ना, और ROI साबित करना — यही मुश्किल और समय खाने वाला हिस्सा है। हम बिल्कुल यही करते हैं, शुरू से आख़िर तक — ताकि नतीजा मिले, जोखिम के बिना।`, `کر سکتے ہیں — اور اوپر کا فائنڈر آپ کو سیدھے ٹولز تک لے جاتا ہے۔ مگر درجنوں اختیارات میں سے چننا، انہیں اپنے POS سے جوڑنا، اور ROI ثابت کرنا — یہی مشکل اور وقت کھانے والا حصہ ہے۔ ہم بالکل یہی کرتے ہیں، شروع سے آخر تک — تاکہ نتیجہ ملے، خطرے کے بغیر۔`],

    // WHAT IT COSTS
    [`What it costs`, `इसका खर्च`, `اس کا خرچ`],
    [`No leap of faith. You see the numbers first.`, `कोई अंधा भरोसा नहीं। पहले आँकड़े देखिए।`, `کوئی اندھا بھروسا نہیں۔ پہلے اعداد دیکھیے۔`],
    [`Whether you need a one-time fix or an ongoing team, we scope it to your restaurant — and you never spend a dollar on faith.`, `चाहे आपको एक बार का सुधार चाहिए या लगातार साथ देने वाली टीम, हम इसे आपके रेस्तराँ के हिसाब से तय करते हैं — और आप कभी भरोसे के भरोसे एक डॉलर भी खर्च नहीं करते।`, `چاہے آپ کو ایک بار کا حل چاہیے یا مسلسل ساتھ دینے والی ٹیم، ہم اسے آپ کے ریستوران کے مطابق طے کرتے ہیں — اور آپ کبھی صرف بھروسے پر ایک ڈالر بھی خرچ نہیں کرتے۔`],
    [`You see the numbers first`, `पहले आँकड़े आपके सामने`, `پہلے اعداد آپ کے سامنے`],
    [`Before anything starts, you get the plan, the cost, and the expected return in plain dollars. If the math doesn't work for you, we don't move.`, `कुछ भी शुरू होने से पहले, आपको योजना, खर्च और अनुमानित फ़ायदा साफ़ डॉलर में मिलता है। अगर हिसाब आपके लिए सही नहीं बैठता, तो हम आगे नहीं बढ़ते।`, `کچھ بھی شروع ہونے سے پہلے، آپ کو منصوبہ، خرچ اور متوقع فائدہ صاف ڈالر میں ملتا ہے۔ اگر حساب آپ کے لیے صحیح نہیں بیٹھتا، تو ہم آگے نہیں بڑھتے۔`],
    [`Built to pay for itself`, `अपना खर्च खुद निकाले`, `اپنا خرچ خود نکالے`],
    [`We start with the fastest-payback fixes — the ones that put money back this month — so the work funds everything that comes after it.`, `हम सबसे जल्दी फ़ायदा देने वाले सुधारों से शुरू करते हैं — जो इसी महीने पैसा वापस लाएँ — ताकि वही काम आगे की हर चीज़ का खर्च निकाल दे।`, `ہم سب سے جلدی فائدہ دینے والے کاموں سے شروع کرتے ہیں — جو اسی مہینے پیسہ واپس لائیں — تاکہ وہی کام آگے کی ہر چیز کا خرچ نکال دے۔`],
    [`No lock-in, ever`, `कभी कोई बंधन नहीं`, `کبھی کوئی پابندی نہیں`],
    [`Month to month. No long contracts, no bricked hardware, no surprise fees. You keep your guests, your data, and your tools — and can walk anytime.`, `महीने-दर-महीने। न लंबे कॉन्ट्रैक्ट, न बेकार हुआ हार्डवेयर, न चौंकाने वाली फ़ीस। आपके ग्राहक, आपका डेटा और आपके टूल आपके पास रहते हैं — और आप कभी भी जा सकते हैं।`, `مہینہ بہ مہینہ۔ نہ لمبے کنٹریکٹ، نہ بیکار ہوا ہارڈویئر، نہ چونکانے والی فیس۔ آپ کے گاہک، آپ کا ڈیٹا اور آپ کے ٹولز آپ کے پاس رہتے ہیں — اور آپ کبھی بھی جا سکتے ہیں۔`],
    [`Founding 5 · performance-first pilot`, `Founding 5 · नतीजे-पहले पायलट`, `Founding 5 · نتیجہ-اول پائلٹ`],
    [`We make you money before we take a dollar.`, `हम पहले आपको कमाई दिलाते हैं, फिर एक डॉलर लेते हैं।`, `ہم پہلے آپ کو کمائی دلاتے ہیں، پھر ایک ڈالر لیتے ہیں۔`],
    [`We're hand-picking <strong>five founding restaurants</strong>. For them, we put real money back in your pocket <em>first</em> — if we don't, you pay nothing. In return you get <strong>founding pricing locked for life</strong>, a direct line to the founder, and first access to everything we build. We only win when you do.`, `हम <strong>पाँच फ़ाउंडिंग रेस्तराँ</strong> ख़ुद चुन रहे हैं। उनके लिए, हम <em>पहले</em> आपकी जेब में असली पैसा डालते हैं — अगर नहीं डाल पाए, तो आप कुछ नहीं देते। बदले में आपको मिलता है <strong>फ़ाउंडिंग कीमत, हमेशा के लिए तय</strong>, संस्थापक से सीधी बात, और हमारी हर नई चीज़ तक पहली पहुँच। हम तभी जीतते हैं जब आप जीतते हैं।`, `ہم <strong>پانچ فاؤنڈنگ ریستوران</strong> خود چن رہے ہیں۔ ان کے لیے، ہم <em>پہلے</em> آپ کی جیب میں اصل پیسہ ڈالتے ہیں — اگر نہ ڈال سکے، تو آپ کچھ نہیں دیتے۔ بدلے میں آپ کو ملتا ہے <strong>فاؤنڈنگ قیمت، ہمیشہ کے لیے طے</strong>، بانی سے سیدھی بات، اور ہماری ہر نئی چیز تک پہلی رسائی۔ ہم تبھی جیتتے ہیں جب آپ جیتتے ہیں۔`],
    [`Apply to be one of the 5`, `इन 5 में शामिल होने के लिए आवेदन करें`, `ان 5 میں شامل ہونے کے لیے درخواست دیں`],
    [`Not ready to apply? The first call is still free — and you'll leave with at least one concrete way to keep more of what you earn. <a href="#contact">Book it here →</a>`, `अभी आवेदन के लिए तैयार नहीं? पहली कॉल फिर भी मुफ़्त है — और आप कम से कम एक ठोस तरीक़ा लेकर जाएँगे जिससे आप अपनी कमाई ज़्यादा बचा सकें। <a href="#contact">यहाँ बुक करें →</a>`, `ابھی درخواست کے لیے تیار نہیں؟ پہلی کال پھر بھی مفت ہے — اور آپ کم از کم ایک ٹھوس طریقہ لے کر جائیں گے جس سے آپ اپنی کمائی زیادہ بچا سکیں۔ <a href="#contact">یہاں بُک کریں →</a>`],

    // CONTACT
    [`Let's find the money your restaurant is leaving on the table.`, `आइए वह पैसा खोजें जो आपका रेस्तराँ यूँ ही छोड़ रहा है।`, `آئیے وہ پیسہ تلاش کریں جو آپ کا ریستوران یونہی چھوڑ رہا ہے۔`],
    [`Tell us a little about your place. We'll personally reply to set up a short video call — and you'll leave with at least one concrete way to keep more of what you earn. Free, no obligation.`, `अपनी जगह के बारे में थोड़ा बताइए। हम ख़ुद जवाब देकर एक छोटी वीडियो कॉल तय करेंगे — और आप कम से कम एक ठोस तरीक़ा लेकर जाएँगे जिससे आप अपनी कमाई ज़्यादा बचा सकें। मुफ़्त, बिना किसी बाध्यता के।`, `اپنی جگہ کے بارے میں تھوڑا بتائیے۔ ہم خود جواب دے کر ایک مختصر ویڈیو کال طے کریں گے — اور آپ کم از کم ایک ٹھوس طریقہ لے کر جائیں گے جس سے آپ اپنی کمائی زیادہ بچا سکیں۔ مفت، بغیر کسی پابندی کے۔`],
    [`Email`, `ईमेल`, `ای میل`],
    [`Phone`, `फ़ोन`, `فون`],
    [`Based in`, `स्थित`, `مقام`],
    [`Name`, `नाम`, `نام`],
    [`Restaurant`, `रेस्तराँ`, `ریستوران`],
    [`Phone <span class="opt">(optional)</span>`, `फ़ोन <span class="opt">(वैकल्पिक)</span>`, `فون <span class="opt">(اختیاری)</span>`],
    [`What would you like to change?`, `आप क्या बदलना चाहेंगे?`, `آپ کیا بدلنا چاہیں گے؟`],
    [`Request my free call`, `मेरी मुफ़्त कॉल का अनुरोध करें`, `میری مفت کال کی درخواست کریں`],
    [`Free &amp; no obligation. We read every message personally.`, `मुफ़्त और बिना किसी बाध्यता के। हम हर संदेश ख़ुद पढ़ते हैं।`, `مفت اور بغیر کسی پابندی کے۔ ہم ہر پیغام خود پڑھتے ہیں۔`],
    [`Your details are used only to reply to you — never shared or sold.`, `आपकी जानकारी सिर्फ़ आपको जवाब देने के लिए इस्तेमाल होती है — कभी साझा या बेची नहीं जाती।`, `آپ کی تفصیلات صرف آپ کو جواب دینے کے لیے استعمال ہوتی ہیں — کبھی شیئر یا فروخت نہیں کی جاتیں۔`],

    // FOOTER
    [`<strong>Keep more of what you earn.</strong> For independent, family-run restaurants — a restaurant family + an engineering team · Spring &amp; Greater Houston, TX.`, `<strong>अपनी कमाई ज़्यादा अपने पास रखें।</strong> आज़ाद, परिवार-संचालित रेस्तराँ के लिए — एक रेस्तराँ परिवार + एक इंजीनियरिंग टीम · स्प्रिंग और ग्रेटर ह्यूस्टन, TX।`, `<strong>اپنی کمائی زیادہ اپنے پاس رکھیں۔</strong> خود مختار، خاندانی ریستوران کے لیے — ایک ریستوران خاندان + ایک انجینئرنگ ٹیم · اسپرنگ اور گریٹر ہیوسٹن، TX۔`],
  ];

  const TX = { hi: {}, ur: {} };
  ROWS.forEach(([e, h, u]) => { const k = norm(e); if (h) TX.hi[k] = h; if (u) TX.ur[k] = u; });

  const SEL = [
    '.nav__links a',
    '.hero .kicker', '.hero__title', '.hero__lead', '.hero__cta a', '.portrait__tag',
    '.creds__item strong', '.creds__item span',
    '.band .h2', '.band .lead', '.band__list li',
    '.stat span',
    '.ctaband p', '.ctaband a',
    '#how .kicker', '#how .h2', '#how .section__head .lead', '.lifecycle li h3', '.lifecycle li p', '.promise',
    '.story .kicker', '.story .h2', '.story__p', '.story__photo figcaption', '.quote__text', '.quote__by',
    '#possible .section__head .kicker', '#possible .section__head .h2', '#possible .section__head .lead',
    '.who__label', '.who__opt',
    '#possible .poss h3', '#possible .poss > p',
    '.possible__more', '#possible .possible__cta',
    '#finder .kicker', '#finder .h2', '#finder .section__head .lead',
    '#faq .kicker', '#faq .h2', '.faq summary', '.faq details > p',
    '#pricing .section__head .kicker', '#pricing .section__head .h2', '#pricing .section__head .lead',
    '#pricing .poss h3', '#pricing .poss > p',
    '.pilot__tag', '.pilot h3', '.pilot p', '.pilot a',
    '#pricing .possible__cta',
    '#contact .kicker', '#contact .h2', '#contact .lead',
    '.contact__list li span',
    '.form label > span', '#formSubmit', '.form__note',
    '.footer__inner p:not(.footer__copy)',
    '.mobilecta a',
  ].join(', ');

  // Dynamic strings used by script.js (persona toggle + finder hint)
  const PERSONA = {
    en: {
      p1: `For a single neighborhood spot, the fastest money is defensive: turn the customers the apps bring you into your own repeat orders, get every call answered, and end the tablet chaos — wins you feel within weeks. <strong>Start with the three marked below.</strong>`,
      p2: `For an established family restaurant, the money is in your regulars and your reputation: bring lapsed guests back, lift your reviews, and grow a higher-margin catering channel. <strong>Start with the three marked below.</strong>`,
      p3: `For 2–10 locations, it's visibility and consistency: recover what the apps owe you across stores, get found everywhere new guests look, and win the customers the apps send you. <strong>Start with the three marked below.</strong>`,
    },
    hi: {
      p1: `एक मोहल्ले की छोटी जगह के लिए, सबसे जल्दी पैसा बचाव में है: ऐप के लाए ग्राहकों को अपने बार-बार के ऑर्डर में बदलें, हर कॉल का जवाब दें, और टैबलेट की अफ़रा-तफ़री ख़त्म करें — फ़ायदा हफ़्तों में दिखेगा। <strong>नीचे चिह्नित तीन से शुरू करें।</strong>`,
      p2: `एक जमे-जमाए फ़ैमिली रेस्तराँ के लिए, पैसा आपके नियमित ग्राहकों और साख में है: छूटे ग्राहक वापस लाएँ, रिव्यू बढ़ाएँ, और ज़्यादा मुनाफ़े वाला कैटरिंग चैनल बढ़ाएँ। <strong>नीचे चिह्नित तीन से शुरू करें।</strong>`,
      p3: `2–10 लोकेशन के लिए, बात है साफ़ नज़र और एकरूपता की: सब दुकानों में ऐप्स का बकाया वसूलें, जहाँ नए ग्राहक देखते हैं वहाँ मिलें, और ऐप के भेजे ग्राहकों को जीतें। <strong>नीचे चिह्नित तीन से शुरू करें।</strong>`,
    },
    ur: {
      p1: `محلے کی ایک چھوٹی جگہ کے لیے، سب سے جلدی پیسہ بچاؤ میں ہے: ایپ کے لائے گاہکوں کو اپنے بار بار کے آرڈر میں بدلیں، ہر کال کا جواب دیں، اور ٹیبلٹ کی افراتفری ختم کریں — فائدہ ہفتوں میں نظر آئے گا۔ <strong>نیچے نشان زدہ تین سے شروع کریں۔</strong>`,
      p2: `ایک جمے جمائے فیملی ریستوران کے لیے، پیسہ آپ کے مستقل گاہکوں اور ساکھ میں ہے: چھوٹے گاہک واپس لائیں، ریویوز بڑھائیں، اور زیادہ منافع والا کیٹرنگ چینل بڑھائیں۔ <strong>نیچے نشان زدہ تین سے شروع کریں۔</strong>`,
      p3: `2–10 مقامات کے لیے، بات ہے صاف نظر اور یکسانیت کی: سب دکانوں میں ایپس کا واجب وصول کریں، جہاں نئے گاہک دیکھتے ہیں وہاں ملیں، اور ایپ کے بھیجے گاہکوں کو جیتیں۔ <strong>نیچے نشان زدہ تین سے شروع کریں۔</strong>`,
    },
  };
  const FINDER_HINT = {
    en: { p: `Set the sentence above to match your place — then see what fits.`, btn: `See what fits my restaurant →` },
    hi: { p: `ऊपर का वाक्य अपनी जगह के हिसाब से सेट करें — फिर देखें क्या सही बैठता है।`, btn: `देखें मेरे रेस्तराँ पर क्या सही बैठता है →` },
    ur: { p: `اوپر کا جملہ اپنی جگہ کے مطابق سیٹ کریں — پھر دیکھیں کیا صحیح بیٹھتا ہے۔`, btn: `دیکھیں میرے ریستوران پر کیا صحیح بیٹھتا ہے →` },
  };

  window.AZL = { lang: 'en', persona: PERSONA, finderHint: FINDER_HINT };

  function translate(lang) {
    document.querySelectorAll(SEL).forEach((el) => {
      if (el.dataset.en === undefined) el.dataset.en = el.innerHTML;
      const key = norm(el.dataset.en);
      el.innerHTML = (lang === 'en') ? el.dataset.en : (TX[lang][key] || el.dataset.en);
    });
  }

  function setLang(lang) {
    window.AZL.lang = lang;
    translate(lang);
    const html = document.documentElement;
    html.setAttribute('lang', lang);
    html.setAttribute('dir', lang === 'ur' ? 'rtl' : 'ltr');
    html.classList.toggle('lang-hi', lang === 'hi');
    html.classList.toggle('lang-ur', lang === 'ur');
    document.querySelectorAll('#lang .lang__opt').forEach((b) => b.classList.toggle('is-active', b.dataset.lang === lang));
    try { localStorage.setItem('azlang', lang); } catch (e) {}
    window.dispatchEvent(new CustomEvent('azlang', { detail: lang }));
  }
  window.AZsetLang = setLang;

  const init = () => {
    document.querySelectorAll('#lang .lang__opt').forEach((b) => b.addEventListener('click', () => setLang(b.dataset.lang)));
    let saved = 'en';
    try { saved = localStorage.getItem('azlang') || 'en'; } catch (e) {}
    setLang(saved);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
