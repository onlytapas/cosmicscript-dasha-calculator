"""
Interpretation text for the numerology report.

The wording here is the content shown to the client verbatim. It is kept
apart from the calculation engine so the two can evolve independently.

Each interpretation is an ordered mapping of section label to paragraph
text, rendered as one titled block per label.
"""

ROOT_INTERPRETATIONS = {
    1: {
        'Ruling Planet': 'Sun (Surya)',
        'Personality & Core Traits': (
            'You are a born leader with a commanding presence and a powerful sense of individuality. '
            'Your personality radiates confidence, authority, and determination. '
            'You have a pioneering spirit — always eager to forge new paths rather than follow others. '
            'You are original in thought, self-reliant, and possess an innate creativity that sets you apart. '
            'People naturally look up to you for guidance and direction.'
        ),
        'Strengths': (
            'Leadership, independence, ambition, creativity, willpower, decisiveness, courage, and strong organisational ability. '
            'You are excellent at initiating projects and inspiring others to rally behind your vision.'
        ),
        'Challenges': (
            'Ego, stubbornness, dominating nature, impatience with slower thinkers, occasional arrogance, and difficulty accepting criticism. '
            'You may struggle to delegate and tend to take on too much yourself.'
        ),
        'Career & Profession': (
            'Government & administration, politics, entrepreneurship, CEO/director roles, creative arts, film & media, military command, independent consulting, and any profession requiring strong leadership and initiative.'
        ),
        'Health': (
            'Vulnerable areas include the heart, eyes, blood circulation, and spine. '
            'Maintain a healthy lifestyle to avoid blood pressure issues and cardiac stress. '
            'Regular exposure to sunlight and warm-toned foods (saffron, honey, oranges) are beneficial.'
        ),
        'Relationships': (
            'You are loyal and protective in love but can be dominating. '
            'You need a partner who respects your independence while offering emotional warmth. '
            'Best compatibility with Root 2, 3, and 9. You thrive when given respect and admiration.'
        ),
    },
    2: {
        'Ruling Planet': 'Moon (Chandra)',
        'Personality & Core Traits': (
            'You are gentle, intuitive, and deeply emotional. '
            'Your sensitivity is your greatest gift — you can sense the feelings and moods of others with remarkable accuracy. '
            'You are a natural peacemaker and diplomat, preferring harmony over conflict. '
            'Your imagination is vivid, and you possess a rich inner world that fuels your creativity and artistic expression.'
        ),
        'Strengths': (
            'Intuition, empathy, diplomacy, cooperation, artistic talent, emotional intelligence, nurturing nature, and adaptability. '
            'You excel in roles that require understanding human emotions and bringing people together.'
        ),
        'Challenges': (
            'Over-sensitivity, mood swings, indecisiveness, dependency on others for emotional validation, shyness, and susceptibility to depression. '
            'You may absorb negativity from your environment and struggle with self-confidence.'
        ),
        'Career & Profession': (
            'Counselling, psychology, nursing, hospitality, poetry & literature, music & performing arts, interior design, diplomacy, public relations, and caregiving professions.'
        ),
        'Health': (
            'Vulnerable areas include the stomach, digestive system, chest, and mental health. '
            'You are prone to water retention, anxiety, and sleep disturbances. '
            'Consume cooling foods (milk, cucumber, coconut water) and practice calming rituals like moonlit walks and meditation.'
        ),
        'Relationships': (
            'You are deeply romantic, loving, and devoted. '
            'You seek emotional security and a soulful connection above all. '
            'You can be possessive when insecure. Best compatibility with Root 1, 3, and 7. '
            'Stable, nurturing partnerships bring out your best.'
        ),
    },
    3: {
        'Ruling Planet': 'Jupiter (Guru/Brihaspati)',
        'Personality & Core Traits': (
            'You are the wise teacher and spiritual guide of the number system. '
            'Your personality is expansive, optimistic, and socially magnetic. '
            'You possess natural wisdom and a philosophical outlook on life. '
            'Generosity flows through you — you believe in sharing knowledge, wealth, and joy with the world. '
            'Your presence uplifts others and you are often the centre of attention in social gatherings.'
        ),
        'Strengths': (
            'Wisdom, optimism, eloquence, spiritual depth, generosity, teaching ability, strong ethics, and a positive outlook. '
            'You are an excellent mentor, guide, and counsellor with a gift for inspiring transformation in others.'
        ),
        'Challenges': (
            'Over-confidence, extravagance, tendency to preach, scattered energy, over-promising, and taking on too many responsibilities. '
            'You may become self-righteous or struggle with financial discipline due to excessive generosity.'
        ),
        'Career & Profession': (
            'Teaching & academia, spiritual leadership, writing & publishing, law & justice, banking & finance, advisory roles, philosophy, religious work, and mentorship programs.'
        ),
        'Health': (
            'Vulnerable areas include the liver, hips, thighs, and blood sugar levels. '
            'Watch for diabetes, obesity, and liver-related conditions. '
            'Include turmeric, yellow foods, and maintain an active lifestyle. '
            'Fasting on Thursdays is considered beneficial.'
        ),
        'Relationships': (
            'You are warm, protective, and seek a partner who values wisdom and spiritual growth. '
            'You tend to guide your partner, which can feel controlling. '
            'Best compatibility with Root 1, 2, and 9. '
            'You need intellectual and spiritual stimulation in love.'
        ),
    },
    4: {
        'Ruling Planet': 'Rahu (North Node of the Moon)',
        'Personality & Core Traits': (
            'You are the revolutionary and unconventional thinker. '
            'Your mind works differently from the mainstream — you see patterns and possibilities that others miss entirely. '
            'You are rebellious by nature, constantly challenging established norms and pushing boundaries. '
            'Your life path is often marked by sudden changes, unexpected events, and transformative experiences that shape a truly unique journey.'
        ),
        'Strengths': (
            'Innovation, determination, persistence, unconventional thinking, technological aptitude, resilience, sharp intellect, and the courage to stand alone. '
            'You excel in breaking old systems and building new ones.'
        ),
        'Challenges': (
            'Restlessness, unpredictability, secretive nature, difficulty fitting into conventional structures, sudden mood changes, obsessive tendencies, and feeling misunderstood by society. '
            'Relationships and stability may take longer to achieve.'
        ),
        'Career & Profession': (
            'Technology & IT, research & development, occult sciences, politics (reformist), aviation, electrical engineering, digital media, astrology, and any field involving innovation or disruption.'
        ),
        'Health': (
            'Vulnerable areas include the nervous system, mental health, skin conditions, and respiratory issues. '
            'You are prone to anxiety, insomnia, and unexplained health patterns. '
            'Grounding practices (walking barefoot, gardening) and routine are essential for stability.'
        ),
        'Relationships': (
            'You are intense, loyal, and deeply passionate but can be unpredictable. '
            'You need a partner who embraces your uniqueness. Best compatibility with Root 5, 6, and 7. '
            'Conventional relationships may feel restrictive — you thrive with a free-spirited partner.'
        ),
    },
    5: {
        'Ruling Planet': 'Mercury (Budh)',
        'Personality & Core Traits': (
            'You are the versatile communicator and eternal youth of the number system. '
            'Your mind is razor-sharp, quick, and constantly seeking new information and experiences. '
            'You are adaptable, witty, and possess a natural charm that makes you excellent in social situations. '
            'Business acumen runs in your veins — you can spot opportunities where others see obstacles. '
            'Change is your natural element.'
        ),
        'Strengths': (
            'Intelligence, communication skills, adaptability, business sense, youthful energy, quick learning, multilingual ability, and networking prowess. '
            'You can master multiple disciplines and excel at connecting people and ideas.'
        ),
        'Challenges': (
            'Restlessness, inconsistency, nervous energy, superficiality, tendency to overthink, fickleness, and difficulty committing to one path. '
            'You may spread yourself too thin and leave projects unfinished.'
        ),
        'Career & Profession': (
            'Business & trading, media & journalism, marketing & advertising, stock market & finance, travel industry, writing, teaching languages, sales, event management, and e-commerce.'
        ),
        'Health': (
            'Vulnerable areas include the nervous system, lungs, skin, and speech-related organs. '
            'You are prone to stress, insomnia, and skin allergies. '
            'Green vegetables, herbal teas, and regular breathing exercises are highly beneficial. '
            'Avoid excessive screen time.'
        ),
        'Relationships': (
            'You are charming, fun-loving, and intellectually stimulating. '
            'You need variety and mental connection in relationships. '
            'Best compatibility with Root 4, 6, and 1. '
            'You value freedom and need a partner who can match your energy and intellect.'
        ),
    },
    6: {
        'Ruling Planet': 'Venus (Shukra)',
        'Personality & Core Traits': (
            'You are the embodiment of love, beauty, and harmony. '
            'Your aesthetic sense is highly refined and you are drawn to everything beautiful — art, music, fashion, nature, and luxurious living. '
            'You carry a magnetic charm and a warm, inviting personality. '
            'Family and relationships are the centre of your universe, and you are deeply committed to your responsibilities toward loved ones.'
        ),
        'Strengths': (
            'Charm, artistic talent, responsibility, nurturing nature, luxury taste, diplomacy, romantic idealism, and strong family values. '
            'You create beauty and harmony wherever you go and have a gift for making others feel loved and valued.'
        ),
        'Challenges': (
            'Vanity, possessiveness, laziness, over-indulgence in pleasures, difficulty saying no, jealousy, and excessive attachment to material comfort. '
            'You may sacrifice your own needs to please others, leading to resentment.'
        ),
        'Career & Profession': (
            'Fashion & design, film & entertainment, luxury brands, hospitality & hotel management, beauty industry, event planning, music, interior decoration, jewellery design, and matrimonial counselling.'
        ),
        'Health': (
            'Vulnerable areas include the kidneys, throat, reproductive system, and skin. '
            'Watch for diabetes, urinary issues, and hormonal imbalances. '
            'Floral scents, rose water, and a balanced diet with sweet fruits are helpful. '
            'Avoid excessive sugar and rich foods.'
        ),
        'Relationships': (
            'You are the ultimate romantic — loyal, devoted, and expressive in love. '
            'You seek beauty and harmony in your partner. Best compatibility with Root 4, 5, and 8. '
            'You thrive in stable, loving relationships with plenty of affection and shared aesthetics.'
        ),
    },
    7: {
        'Ruling Planet': 'Ketu (South Node of the Moon)',
        'Personality & Core Traits': (
            'You are the mystic, the seeker, and the philosopher. '
            'Your mind is drawn to the unseen realms — spirituality, metaphysics, and the deeper meaning of existence. '
            'You possess a mysterious aura that both fascinates and puzzles others. '
            'Introspection and solitude are essential for your inner growth. '
            'You have powerful psychic and intuitive abilities that can guide you if you learn to trust them.'
        ),
        'Strengths': (
            'Spiritual depth, analytical mind, intuition, research ability, psychic sensitivity, wisdom, patience, and detachment from materialism. '
            'You excel at uncovering hidden truths and conducting deep research in any field.'
        ),
        'Challenges': (
            'Isolation, escapism, difficulty expressing emotions, aloofness, pessimism, trust issues, and tendency toward loneliness. '
            'You may struggle with worldly responsibilities and find it hard to connect emotionally with others.'
        ),
        'Career & Profession': (
            'Spiritual teaching, research & academia, occult sciences & astrology, psychology, philosophy, healing arts (Reiki, Ayurveda), writing, archaeology, marine science, and monastic/contemplative life.'
        ),
        'Health': (
            'Vulnerable areas include the digestive system, skin, mental health, and mysterious/hard-to-diagnose conditions. '
            'You are prone to psychosomatic illnesses and spiritual crises. '
            'Meditation, fasting, and a sattvic (pure vegetarian) diet bring healing. Avoid intoxicants.'
        ),
        'Relationships': (
            'You are deeply spiritual in love — seeking a soulmate rather than just a partner. '
            'You can appear distant but feel profoundly. Best compatibility with Root 4, 6, and 2. '
            'You need space and understanding in relationships, and connect best through shared spiritual interests.'
        ),
    },
    8: {
        'Ruling Planet': 'Saturn (Shani)',
        'Personality & Core Traits': (
            'You are the embodiment of discipline, karma, and material mastery. '
            'Your life is governed by the law of cause and effect — every effort you make eventually yields results, though often with delay. '
            'You possess immense inner strength, endurance, and a sense of justice that is unwavering. '
            'Authority comes naturally to you, and you are drawn to positions of power and responsibility. '
            'Your journey involves mastering patience and persistence.'
        ),
        'Strengths': (
            'Discipline, ambition, organisational skills, sense of justice, endurance, strategic thinking, financial acumen, and integrity. '
            'You build empires through sheer hard work and can manage large operations with precision.'
        ),
        'Challenges': (
            'Delays and obstacles, pessimism, rigidity, loneliness, materialistic tendencies, controlling nature, and karmic debts. '
            'You may face more hardships than others early in life, but your rewards come in the second half of life with compound interest.'
        ),
        'Career & Profession': (
            'Law & judiciary, real estate, mining & metals, construction, large-scale industry, politics, banking, civil services, agriculture, and any profession requiring long-term commitment and systematic effort.'
        ),
        'Health': (
            'Vulnerable areas include bones, joints, teeth, knees, and chronic conditions. '
            'You are prone to arthritis, calcium deficiency, and depression. '
            'Regular exercise, calcium-rich foods, and a disciplined routine are essential. '
            'Saturdays may be energetically heavier — rest and reflect.'
        ),
        'Relationships': (
            'You are loyal, committed, and protective but can be emotionally reserved. '
            'You express love through actions rather than words. Best compatibility with Root 5, 6, and 4. '
            'Late marriages tend to be more successful. '
            'You need a patient, mature partner who values stability.'
        ),
    },
    9: {
        'Ruling Planet': 'Mars (Mangal)',
        'Personality & Core Traits': (
            'You are the warrior, the humanitarian, and the force of dynamic action. '
            'Your personality is intense, courageous, and driven by a deep desire to serve and protect. '
            'You possess enormous willpower and a fiery temperament that can move mountains. '
            'You are drawn to causes larger than yourself and have a natural instinct to fight for justice and the welfare of others.'
        ),
        'Strengths': (
            'Courage, determination, compassion, leadership in action, physical vitality, protective instincts, generosity, and selfless service. '
            'You are a natural commander and excel in situations that demand quick decisions and bold action.'
        ),
        'Challenges': (
            'Aggression, impulsiveness, short temper, domineering behaviour, impatience, tendency toward conflict, and emotional intensity. '
            'You may burn bridges due to hasty reactions and struggle with anger management.'
        ),
        'Career & Profession': (
            'Military & defence, police & law enforcement, surgery & medicine, sports & athletics, firefighting, engineering, martial arts, social activism, and any profession requiring courage and physical energy.'
        ),
        'Health': (
            'Vulnerable areas include blood, head, muscles, and the inflammatory system. '
            'You are prone to fevers, accidents, surgeries, and blood-related issues. '
            'Regular physical exercise, martial arts, and iron-rich foods are beneficial. '
            'Avoid excessive spicy food and channel anger constructively.'
        ),
        'Relationships': (
            'You are passionate, protective, and intensely loyal. You fight fiercely for those you love. '
            'However, your intensity can overwhelm partners. Best compatibility with Root 1, 3, and 2. '
            'You need a partner who can handle your fire and match your passion for life.'
        ),
    },
}

DESTINY_INTERPRETATIONS = {
    1: {
        'Ruling Planet': 'Sun (Surya)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to lead, innovate, and inspire. '
            'The universe has placed you on a path where your individuality and originality will be your greatest assets. '
            'You are meant to pioneer new ideas, create new systems, and stand as a beacon of confidence and determination for others to follow. '
            "Independence is not just a trait — it is your destiny's core requirement. "
            'The more you embrace your unique identity, the more aligned your life becomes.'
        ),
        'Career & Life Direction': (
            'You are destined for positions of authority and creative leadership. '
            'Your path leads toward entrepreneurship, government roles, executive positions, or any domain where you can exercise independent decision-making. '
            'Creative industries, media, and technology are especially favourable. '
            'Success comes when you take initiative rather than waiting for permission.'
        ),
        'Key Life Lessons': (
            'Learning to balance leadership with humility, independence with collaboration, and ambition with compassion. '
            'Your destiny tests you through situations that require courage, self-belief, and the willingness to stand alone when necessary.'
        ),
        'Opportunities & Timing': (
            'Major breakthroughs often come in years ruled by 1, 2, or 9. '
            'Your destiny favours starting new ventures and taking bold steps. '
            'The second half of life usually brings greater recognition and achievement as your leadership qualities fully mature.'
        ),
    },
    2: {
        'Ruling Planet': 'Moon (Chandra)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to bring harmony, healing, and emotional connection to the world. '
            'You are placed on this earth to be the bridge between opposing forces — mediating, nurturing, and creating peace. '
            'Your path is not one of loud leadership but of quiet influence. '
            'Through sensitivity, empathy, and intuition, you will touch lives in profound and lasting ways.'
        ),
        'Career & Life Direction': (
            'Your destiny leads toward roles in counselling, healing arts, creative expression, diplomacy, and care-giving. '
            'Partnerships and collaborations are central to your success — you thrive when working alongside others rather than in isolation. '
            'Music, poetry, psychology, hospitality, and nursing are deeply aligned with your life purpose.'
        ),
        'Key Life Lessons': (
            'Overcoming emotional dependency, building inner confidence, and learning to set healthy boundaries while maintaining your compassionate nature. '
            'Your destiny challenges you to find strength in softness and power in vulnerability.'
        ),
        'Opportunities & Timing': (
            'Significant life events and opportunities often arrive on Mondays and in years governed by 2, 1, or 7. '
            'Your destiny unfolds gradually — patience is essential. '
            'Emotional maturity unlocks your greatest gifts in relationships and career.'
        ),
    },
    3: {
        'Ruling Planet': 'Jupiter (Guru/Brihaspati)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to teach, guide, and uplift humanity through wisdom and spiritual understanding. '
            'You are a natural philosopher and knowledge bearer — the universe has designed your path so that everything you learn becomes a gift you share with others. '
            'Your optimism and expansive worldview are not accidental; they are tools your destiny requires to fulfil its purpose of spreading light and knowledge.'
        ),
        'Career & Life Direction': (
            'Your destiny draws you toward education, publishing, spiritual leadership, advisory roles, law, and finance. '
            'You may become a mentor, author, professor, or spiritual guide. '
            'Careers in banking, judiciary, and counselling are also highly favoured. '
            "Your life's work involves expanding minds and opening hearts."
        ),
        'Key Life Lessons': (
            'Avoiding overconfidence and scattered energy. '
            'Learning to channel your vast potential into focused, sustained effort rather than spreading across too many ventures. '
            'Financial discipline and discernment in generosity are recurring themes.'
        ),
        'Opportunities & Timing': (
            'Thursdays and years governed by 3, 1, or 9 bring significant opportunities. '
            'Your destiny generally promises prosperity and recognition, especially when you align with teaching, mentoring, or advisory roles. '
            'The period between 30-50 is often your most productive.'
        ),
    },
    4: {
        'Ruling Planet': 'Rahu (North Node of the Moon)',
        'Life Purpose & Destiny Path': (
            'Your destiny is one of transformation, disruption, and unconventional achievement. '
            'The universe has given you a path that rarely follows straight lines — instead, it twists and turns through unexpected territories, each experience shaping you into a powerful agent of change. '
            'You are here to break outdated structures and build innovative ones in their place.'
        ),
        'Career & Life Direction': (
            'Technology, research, reform movements, digital innovation, aviation, and unconventional sciences are your destined domains. '
            'You may find success in politics (as a reformer), occult studies, or emerging industries. '
            'Your path often involves being ahead of your time — what seems eccentric today may become mainstream tomorrow because of your efforts.'
        ),
        'Key Life Lessons': (
            'Embracing instability as a teacher, finding inner peace amidst external chaos, and learning to trust the process even when the path is unclear. '
            'Your destiny demands resilience, adaptability, and the courage to be different.'
        ),
        'Opportunities & Timing': (
            'Sudden and unexpected opportunities define your timeline. '
            'Saturdays and periods governed by 4, 5, or 7 can bring breakthroughs. '
            "Your life often has distinct 'before and after' moments — major transformations that redirect your entire trajectory."
        ),
    },
    5: {
        'Ruling Planet': 'Mercury (Budh)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to communicate, connect, and experience the full diversity of life. '
            'You are the cosmic messenger — meant to bridge cultures, ideas, and people. '
            'Your restless energy is not a flaw but a feature of your destiny, driving you to explore, learn, and share knowledge across boundaries. '
            'The world becomes richer through your experiences and the connections you facilitate.'
        ),
        'Career & Life Direction': (
            'Business, international trade, media, journalism, writing, public speaking, and travel-related industries are your natural domains. '
            'Digital marketing, e-commerce, stocks and trading, and multilingual roles are especially favoured. '
            'Your destiny supports multiple career streams and diverse income sources.'
        ),
        'Key Life Lessons': (
            'Developing consistency and depth alongside your natural breadth. '
            'Learning to commit fully to chosen paths while maintaining your versatility. '
            'Your destiny challenges you to transform surface-level knowledge into genuine wisdom.'
        ),
        'Opportunities & Timing': (
            'Wednesdays and years governed by 5, 1, or 6 bring important opportunities. '
            'Your destiny accelerates in your 20s and 30s when your energy and communication skills are at their peak. '
            'Financial success often comes through clever timing and diverse investments.'
        ),
    },
    6: {
        'Ruling Planet': 'Venus (Shukra)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to create beauty, nurture love, and bring harmony to every sphere of life. '
            'You are here to demonstrate that luxury and spirituality can coexist, that responsibility and pleasure are not opposites. '
            "The universe has designed your path to be rich with relationships, artistic expression, and material comfort — all as vehicles for your soul's growth."
        ),
        'Career & Life Direction': (
            'Fashion, design, entertainment, hospitality, luxury brands, beauty industry, and the arts are your destined fields. '
            'Counselling (especially relationship and family), event management, interior decoration, and culinary arts are also deeply aligned. '
            'Your career often involves making things more beautiful, harmonious, or pleasurable.'
        ),
        'Key Life Lessons': (
            'Balancing attachment with detachment, pleasure with purpose, and self-indulgence with service. '
            'Your destiny tests you through relationships — learning to love without possessing and to give without losing yourself.'
        ),
        'Opportunities & Timing': (
            'Fridays and years governed by 6, 5, or 8 are especially significant. '
            'Your destiny often brings early romantic experiences and mid-life material success. '
            'The key is maintaining balance — too much indulgence delays your destiny, while disciplined creativity accelerates it.'
        ),
    },
    7: {
        'Ruling Planet': 'Ketu (South Node of the Moon)',
        'Life Purpose & Destiny Path': (
            'Your destiny is one of spiritual seeking, inner transformation, and the pursuit of hidden truths. '
            'You are not here to chase the material world but to understand what lies beneath it. '
            'Your path is contemplative, mystical, and deeply personal — the answers you seek cannot be found in textbooks but in meditation, introspection, and direct spiritual experience.'
        ),
        'Career & Life Direction': (
            'Research, spiritual teaching, healing arts, psychology, philosophy, and occult sciences define your professional destiny. '
            'You may also excel in marine sciences, archaeology, or any field requiring deep investigation. '
            'Your work often involves uncovering what is hidden — whether scientific truths, psychological patterns, or spiritual mysteries.'
        ),
        'Key Life Lessons': (
            'Balancing spiritual aspiration with worldly responsibility. '
            'Learning to connect with others despite your natural inclination toward solitude. '
            'Your destiny challenges you to share your profound insights rather than keeping them locked within.'
        ),
        'Opportunities & Timing': (
            'Mondays and years governed by 7, 2, or 4 are pivotal. '
            'Your destiny often involves one or two major spiritual awakenings that completely transform your worldview. '
            'Success in the material world comes indirectly — when you stop chasing it and focus on your inner work.'
        ),
    },
    8: {
        'Ruling Planet': 'Saturn (Shani)',
        'Life Purpose & Destiny Path': (
            'Your destiny is governed by the great cosmic law of karma — you reap exactly what you sow, often with compound interest. '
            'Your path is one of power, authority, and systematic achievement, but it demands extraordinary patience and discipline. '
            'The universe tests you more rigorously than others because your destiny involves wielding significant influence and responsibility.'
        ),
        'Career & Life Direction': (
            'Law, judiciary, real estate, industrial leadership, politics, banking, and large-scale enterprise management are your destined fields. '
            'Construction, mining, agriculture, and strategic planning roles are also deeply aligned. '
            'Your career trajectory is often slow but exponential — modest beginnings leading to powerful positions.'
        ),
        'Key Life Lessons': (
            'Patience as the supreme virtue. '
            'Learning that delays are not denials but preparations for greater responsibility. '
            'Your destiny requires you to master discipline, endure hardship gracefully, and understand that true power comes from service, not domination.'
        ),
        'Opportunities & Timing': (
            'Saturdays and years governed by 8, 5, or 6 are significant. '
            "Your destiny is famously 'late-blooming' — the period after 35-40 typically brings the greatest rewards. "
            "Trust the process: every struggle in the first half of life is building the foundation for the second half's triumphs."
        ),
    },
    9: {
        'Ruling Planet': 'Mars (Mangal)',
        'Life Purpose & Destiny Path': (
            'Your destiny is to serve humanity through courageous action and selfless dedication. '
            'You are a spiritual warrior — placed on this earth to fight for justice, protect the vulnerable, and lead from the front when courage is needed most. '
            'Your path demands physical vitality, emotional intensity, and a willingness to sacrifice personal comfort for the greater good.'
        ),
        'Career & Life Direction': (
            'Military and defence services, law enforcement, surgery, sports, social activism, and emergency services are your destined domains. '
            'Engineering, martial arts instruction, and humanitarian organisations are also deeply aligned. '
            'Your career often involves high-stakes situations where your courage and quick decision-making save the day.'
        ),
        'Key Life Lessons': (
            'Channelling aggression into constructive action, managing intense emotions, and learning that true strength includes gentleness. '
            'Your destiny tests you through conflicts that require you to fight wisely, not just fiercely.'
        ),
        'Opportunities & Timing': (
            'Tuesdays and years governed by 9, 1, or 3 are most significant. '
            'Your destiny accelerates during periods of challenge — obstacles that break others make you stronger. '
            'Physical fitness and mental discipline are essential tools for fulfilling your powerful destiny.'
        ),
    },
}

# Favourable attributes keyed by number (apply to Root and Destiny alike).
FAVOURABLE_COLOURS = {
    1: 'Gold, Orange, Yellow',
    2: 'White, Silver, Cream',
    3: 'Yellow, Orange, Saffron',
    4: 'Blue-Grey, Electric Blue',
    5: 'Green, Light Green',
    6: 'Pink, White, Pastel',
    7: 'Grey-Green, Smoky White',
    8: 'Dark Blue, Black, Violet',
    9: 'Red, Coral, Crimson',
}

FAVOURABLE_DAYS = {
    1: 'Sunday',
    2: 'Monday',
    3: 'Thursday',
    4: 'Saturday, Sunday',
    5: 'Wednesday',
    6: 'Friday',
    7: 'Monday',
    8: 'Saturday',
    9: 'Tuesday',
}

FRIENDLY_NUMBERS = {
    1: '2, 3, 9',
    2: '1, 3',
    3: '1, 2, 9',
    4: '5, 6, 7',
    5: '4, 6',
    6: '4, 5, 8',
    7: '4, 6',
    8: '5, 6',
    9: '1, 3',
}

NEUTRAL_NUMBERS = {
    1: '5',
    2: '6, 7, 9',
    3: '4, 7, 8',
    4: '1, 2, 3, 9',
    5: '1, 3, 7, 9',
    6: '3, 7, 9',
    7: '1, 2, 3, 5',
    8: '3, 7, 9',
    9: '2, 5, 7',
}

ENEMY_NUMBERS = {
    1: '4, 6, 8',
    2: '4, 5, 8',
    3: '5, 6',
    4: '8',
    5: '2, 8',
    6: '1, 2',
    7: '8, 9',
    8: '1, 2, 4, 7',
    9: '4, 6, 8',
}
