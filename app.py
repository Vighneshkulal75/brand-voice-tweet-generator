import json
import html
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

st.set_page_config(
    page_title="Brand Voice Tweet Generator",
    page_icon="✍️",
    layout="centered"
)

# -------------------- DESIGN --------------------
st.markdown("""
<style>
html, body, .stApp, [class*="st-"], button, input, textarea {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif !important;
}
.stApp { background: #faf8f5; font-size: 16px; }
[data-testid="stMainBlockContainer"] {
    max-width: 760px;
    padding: 1.5rem 1rem 3rem;
}
h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #1c1b1a; }
h2, h3 {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: #1c1b1a;
    margin: 0 0 .5rem !important;
    padding: 0 !important;
}
p, li { font-size: 16px !important; line-height: 1.5 !important; color: #1c1b1a; }
label, label p {
    font-size: .85rem !important;
    font-weight: 400 !important;
    color: #6b6761 !important;
}
.app-subtitle { color: #6b6761; font-size: 16px; margin: -4px 0 14px; }

/* Pill tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: none !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: #ffffff !important;
    border: 1px solid #e4dfd8 !important;
    border-radius: 999px !important;
    padding: 8px 14px !important;
    height: auto !important;
    color: #1c1b1a !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] p {
    font-size: 16px !important;
    color: #1c1b1a !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    background: #d9480f !important;
    border-color: #d9480f !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {
    color: #ffffff !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #faf8f5 !important;
    border: 1px solid #e4dfd8 !important;
    border-radius: 8px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #faf8f5 !important;
    border: 1px solid #e4dfd8 !important;
    border-radius: 8px !important;
}

/* Form and cards */
div[data-testid="stForm"] {
    background: #ffffff;
    border: 1px solid #e4dfd8;
    border-radius: 12px;
    padding: 16px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e4dfd8 !important;
    border-radius: 12px;
}
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stDownloadButton"] button {
    background: #d9480f;
    color: #ffffff;
    border: 0;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 20px;
}
div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {
    background: #b83a08;
    color: #ffffff;
}
div[data-testid="stFormSubmitButton"] button p,
div[data-testid="stDownloadButton"] button p {
    color: #ffffff !important;
}

/* Tweets */
.tweet-label {
    display: inline-block;
    background: #fff0e8;
    color: #d9480f;
    border-radius: 999px;
    padding: 2px 8px;
    font-size: .72rem;
    margin-bottom: 4px;
}
.tweet-text { font-size: 16px; line-height: 1.5; color: #1c1b1a; }
.voice-label { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
.brand-meta { color: #6b6761; font-size: .85rem; margin: -4px 0 8px; }
hr { border: 0; border-top: 1px solid #e4dfd8; margin: .5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------- COPY BUTTON --------------------
def copy_button(text, key):
    # JSON encoding protects quotes and most special characters.
    safe_text = json.dumps(text, ensure_ascii=True).replace(
        "</", "<\\/"
    )

    components.html(
        f"""
        <div style="display:flex;justify-content:flex-end;align-items:center;
                    font-family:system-ui,sans-serif;">
          <span id="status-{key}"
            style="font-size:11px;margin-right:6px;color:#248342;"></span>
          <button id="copy-{key}"
            style="background:none;border:1px solid #e4dfd8;
                   border-radius:6px;padding:4px 8px;cursor:pointer;
                   color:#6b6761;font-size:13px;
                   font-family:system-ui,sans-serif;">
            Copy
          </button>
        </div>
        <script>
        const btn = document.getElementById("copy-{key}");
        const status = document.getElementById("status-{key}");
        const textToCopy = {safe_text};

        btn.addEventListener("click", async () => {{
          try {{
            await navigator.clipboard.writeText(textToCopy);
            status.textContent = "Copied!";
          }} catch (err) {{
            const area = document.createElement("textarea");
            area.value = textToCopy;
            area.style.position = "fixed";
            area.style.left = "-9999px";
            document.body.appendChild(area);
            area.select();
            const success = document.execCommand("copy");
            area.remove();
            status.textContent = success ? "Copied!" : "Select text manually";
          }}
          setTimeout(() => {{ status.textContent = ""; }}, 1500);
        }});
        </script>
        """,
        height=35,
        scrolling=False
    )

# -------------------- TWEET ROW --------------------
def show_tweet(tweet, index, prefix="tweet"):
    style = tweet.get("style", "Tweet")
    text = tweet.get("text", "")

    col1, col2 = st.columns([5, 2])

    with col1:
        st.markdown(
            f'<span class="tweet-label">{html.escape(style)}</span>'
            f'<div class="tweet-text">{html.escape(text)}</div>',
            unsafe_allow_html=True
        )

    with col2:
        copy_button(text, f"{prefix}-{index}")

# -------------------- HEADER --------------------
st.markdown(
    "<h1 style='margin-bottom:4px;'>Brand Voice Tweet Generator</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='app-subtitle'>"
    "Enter a brand, get a voice summary and 10 on-brand tweets."
    "</div>",
    unsafe_allow_html=True
)

tool_tab, sample_tab, approach_tab = st.tabs(
    ["Tool", "Sample outputs", "Approach"]
)

# -------------------- TOOL TAB --------------------
with tool_tab:
    with st.form("brand_form"):
        col1, col2 = st.columns(2)

        with col1:
            brand = st.text_input(
                "Brand name (optional)",
                placeholder="e.g. Zomato"
            )

        with col2:
            industry = st.text_input(
                "Industry / category (optional)",
                placeholder="e.g. Food delivery"
            )

        objective = st.selectbox(
            "Campaign objective",
            [
                "Engagement",
                "Brand awareness",
                "Promotion / sales",
                "Product launch",
                "Education / value"
            ]
        )

        products = st.text_area(
            "About the brand's products",
            placeholder=(
                "Describe products, audience, known brand traits, "
                "and any facts the tweets may use."
            ),
            height=100
        )

        tone = st.selectbox(
            "Preferred tone",
            [
                "Let AI decide",
                "Funny and witty",
                "Friendly and conversational",
                "Bold and inspiring",
                "Professional and informative",
                "Premium and elegant"
            ]
        )

        submitted = st.form_submit_button(
            "Generate 10 tweets"
        )

    if submitted:
        if not any([
            brand.strip(),
            industry.strip(),
            products.strip()
        ]):
            st.warning(
                "Enter a brand name, industry, or product description."
            )
        else:
            try:
                client = Groq(
                    api_key=st.secrets["GROQ_API_KEY"]
                )

                prompt = f"""
You are an expert brand strategist and social media copywriter.

Brand: {brand or "Not specified"}
Industry: {industry or "Not specified"}
Products/services and context: {products or "Not specified"}
Campaign objective: {objective}
Preferred tone: {tone}

Infer the likely voice from the supplied information.
Do not claim to have analysed live social media posts.
Do not invent discounts, prices, product specifications,
research, statistics, delivery promises or current offers.
Only state specific facts supported by the input or reliable
general knowledge. When unsure, write without that claim.

Return 3 to 4 concise brand voice bullet points, the likely
audience, and 2 to 4 content themes.

Generate exactly 10 distinct tweets, each under 280 characters:
3 Conversational, 3 Promotional, 2 Witty, 2 Informative.
Keep the wording varied, engaging and suitable for X.
Avoid repetitive openings and excessive hashtags.

Return valid JSON:
{{
  "brand_voice": ["point 1", "point 2", "point 3"],
  "audience": "likely audience",
  "content_themes": ["theme 1", "theme 2"],
  "tweets": [
    {{"number": 1, "style": "Conversational", "text": "Tweet"}}
  ]
}}

Use only these style labels: Conversational, Promotional,
Witty, Informative. Return exactly 10 tweet objects.
"""

                with st.spinner("Generating your brand voice and tweets..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a careful brand strategist. "
                                    "Follow the JSON format and avoid "
                                    "unsupported factual claims."
                                )
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )

                result = json.loads(
                    response.choices[0].message.content
                )

                st.session_state["brandvoice_result"] = result
                st.session_state["brandvoice_name"] = (
                    brand.strip() or industry.strip() or "Your brand"
                )
                st.session_state["brandvoice_industry"] = industry
                st.session_state["brandvoice_objective"] = objective
                st.session_state["brandvoice_products"] = products

            except Exception as error:
                st.error("Tweet generation failed.")
                st.caption(str(error))

    result = st.session_state.get("brandvoice_result")

    if result:
        st.markdown("---")

        st.markdown(
            f"### {html.escape(st.session_state.get('brandvoice_name', 'Your brand'))}",
            unsafe_allow_html=True
        )

        meta = (
            f"Industry: {st.session_state.get('brandvoice_industry') or 'Not specified'}. "
            f"Objective: {st.session_state.get('brandvoice_objective', '')}. "
            f"Products: {st.session_state.get('brandvoice_products') or 'Not specified'}."
        )
        st.markdown(
            f'<div class="brand-meta">{html.escape(meta)}</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown(
                '<div class="voice-label">Brand voice</div>',
                unsafe_allow_html=True
            )

            for point in result.get("brand_voice", [])[:4]:
                st.markdown(f"- {point}")

            st.markdown("**Target audience**")
            st.write(result.get("audience", "Not specified"))

            st.markdown("**Content themes**")
            st.write(", ".join(result.get("content_themes", [])))

        tweets = result.get("tweets", [])

        with st.container(border=True):
            st.markdown(f"### {len(tweets)} tweets")

            if len(tweets) != 10:
                st.warning(
                    f"The model returned {len(tweets)} tweets instead "
                    "of 10. Try generating again."
                )

            for index, tweet in enumerate(tweets, start=1):
                show_tweet(tweet, index, "generated")
                if index < len(tweets):
                    st.markdown("<hr>", unsafe_allow_html=True)

        st.download_button(
            "Download results as JSON",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name="brand_tweets.json",
            mime="application/json"
        )

# -------------------- SAMPLE OUTPUTS TAB --------------------
with sample_tab:
    st.markdown("### Sample outputs")
    st.caption(
        "Illustrative examples for two different brands. "
        "These are sample copy, not official brand statements."
    )

    sample_brands = [
        {
            "name": "Zomato",
            "industry": "Food delivery",
            "objective": "Engagement",
            "products": "Restaurant discovery, food delivery, table booking",
            "voice": [
                "Tone: witty, self-aware and playful",
                "Audience: young urban foodies",
                "Themes: cravings, food humour and restaurant discovery",
                "Style: short punchy lines, casual language and light emoji"
            ],
            "tweets": [
                ("Conversational", "Biryani or pizza at 1 AM? Asking for a friend. The friend is you."),
                ("Witty", "Your fridge: empty. Your ambition: empty. Your food cart: full."),
                ("Promotional", "Your next favourite meal might be closer than you think. Explore local food spots."),
                ("Informative", "Tip: read recent restaurant reviews and check menu photos before trying somewhere new."),
                ("Witty", "I'll just have a light dinner — last words before ordering dessert."),
                ("Conversational", "What's the one dish you'd defend in a debate? Tell us below."),
                ("Promotional", "Rainy evening, cosy sofa, favourite food. Sounds like a plan."),
                ("Witty", "Me: I'm saving money. Also me: opening a food app just to look."),
                ("Informative", "Not sure what to eat? Explore cuisines and restaurant menus to find your next meal."),
                ("Conversational", "Cooking is just ordering with extra steps.")
            ]
        },
        {
            "name": "Tanishq",
            "industry": "Jewellery",
            "objective": "Promotion",
            "products": "Gold and diamond jewellery, wedding and festive collections",
            "voice": [
                "Tone: elegant, warm and emotional",
                "Audience: families, couples and gift-givers",
                "Themes: celebrations, craftsmanship and meaningful moments",
                "Style: polished sentences, minimal slang and restrained emoji"
            ],
            "tweets": [
                ("Conversational", "Which piece in your family has a story older than you? We'd love to listen."),
                ("Promotional", "This festive season, begin a new tradition. Explore jewellery for meaningful moments."),
                ("Informative", "When buying gold jewellery, ask about hallmarking and check the relevant certification."),
                ("Witty", "Some gifts say 'I remember.' The best ones say 'I know you.'"),
                ("Promotional", "Crafted for special moments. Discover designs for celebrations big and small."),
                ("Conversational", "A wedding is a hundred small moments. Which one are you looking forward to most?"),
                ("Informative", "Store jewellery separately and keep it away from perfume to help care for your pieces."),
                ("Witty", "A subtle hint for the season: a small box can say a lot."),
                ("Promotional", "Looking for something personal? Explore designs and choose a piece that feels like you."),
                ("Conversational", "Wishing you a celebration filled with the moments you'll treasure.")
            ]
        }
    ]

    for brand_index, sample in enumerate(sample_brands):
        st.markdown(f"### {sample['name']}")

        st.markdown(
            f'<div class="brand-meta">Industry: {html.escape(sample["industry"])}. '
            f'Objective: {html.escape(sample["objective"])}. '
            f'Products: {html.escape(sample["products"])}.</div>',
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown(
                '<div class="voice-label">Brand voice</div>',
                unsafe_allow_html=True
            )
            for point in sample["voice"]:
                st.markdown(f"- {point}")

        with st.container(border=True):
            st.markdown("### 10 tweets")
            for index, (style, text) in enumerate(
                sample["tweets"], start=1
            ):
                show_tweet(
                    {"style": style, "text": text},
                    index,
                    f"sample{brand_index}"
                )
                if index < len(sample["tweets"]):
                    st.markdown("<hr>", unsafe_allow_html=True)

    st.caption(
        "Sample copy is illustrative and should be reviewed before publication."
    )

# -------------------- APPROACH TAB --------------------
with approach_tab:
    with st.container(border=True):
        st.markdown("### 1. How brand voice is analysed")
        st.write(
            "Prompt-based inference. The model infers likely tone, "
            "audience, themes and writing habits from the brand name, "
            "industry, product description and campaign objective. "
            "It does not claim to have analysed live social posts."
        )

        st.markdown("### 2. How prompts are structured")
        st.write(
            "A structured prompt contains the role and brand inputs, "
            "a brand voice analysis task, and a tweet-generation task. "
            "It requests a concise voice summary and exactly 10 tweets "
            "in four styles: 3 conversational, 3 promotional, 2 witty, "
            "and 2 informative. The prompt encourages concise writing "
            "and discourages unsupported product claims. The application "
            "checks the total number of generated tweets and displays "
            "a warning if the count differs from 10. The requested style "
            "distribution is guided by the prompt rather than independently "
            "validated by the code."
        )

        st.markdown("### 3. Tools used")
        st.write(
            "Python, Streamlit for the web interface, Groq API for "
            "language-model inference, and the OpenAI GPT-OSS 120B model "
            "served through Groq. Streamlit components provide the "
            "individual copy buttons."
        )

        st.markdown("### 4. Design choices")
        st.write(
            "The interface uses a compact centred layout, warm neutral "
            "background, orange accents, rounded cards, and separate "
            "Tool, Sample outputs and Approach tabs. Each tweet has a "
            "copy button. Results can also be downloaded as JSON."
        )

        st.markdown("### 5. Limitations and review")
        st.write(
            "Brand voice is inferred from the brief and is not a verified "
            "brand audit. AI output may still contain mistakes, so review "
            "claims and wording before publishing."
        )

