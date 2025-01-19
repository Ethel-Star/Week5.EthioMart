import re

class CoNLLFormatter:
    def __init__(self):
        self.inside_product = False
        self.inside_location = False
        self.inside_price = False

    def tokenize_message(self, message):
        """Tokenizes the input message into individual tokens."""
        return re.findall(r'\S+', message)

    def label_token(self, token):
        """Labels a single token based on its type (Product, Location, Price)."""
        # Check for price (e.g., 'ዋጋ 1000 ብር')
        if re.match(r'^\d+(\.\d{1,2})?$|ዋጋ|ብር', token):
            if not self.inside_price:
                self.inside_price = True
                self.inside_product = self.inside_location = False  # Reset other flags
                return f"{token} B-PRICE"
            return f"{token} I-PRICE"

        # Check for location
        elif any(loc in token for loc in [
            'ቁ1መገናኛ', 'ቁ2ፒያሳ', 'ጊዮርጊስ', 'ደፋር', 
            'ራመት_ታቦር_ኦዳ_ህንፃ', 'ሱቅ', 'የቴሌግራም', 
            'አዲስ አበባ', 'ቦሌ', 'ፒያሳ', 
            'አደባባይ', 'መሰረት', 'ሞል', 
            'ፎቅ', 'ቢሮ', 'ቱንባባ', 'ቀርንጫፍ'
        ]):
            if not self.inside_location:
                self.inside_location = True
                self.inside_product = self.inside_price = False  # Reset other flags
                return f"{token} B-LOC"
            return f"{token} I-LOC"

        # Check for product
        elif any(product in token for product in [
            'ሽንኩርት', 'ጫማ', 'ቦርሳ', 
            'ዕቃ', 'ታብሌቱ', 'ቤት', 
            'ለልጅዎ', 'እርሳስ', 
            'የህፃናት','መመገቢያ', 'ጡጦ', 
            'ከብረት የተሰራ ጫማ'
        ]):
            if not self.inside_product:
                self.inside_product = True
                self.inside_location = self.inside_price = False  # Reset other flags
                return f"{token} B-PRODUCT"
            return f"{token} I-PRODUCT"

        # Outside any entity
        return f"{token} O"

    def label_message(self, message):
        """Labels the tokens of a message in CoNLL format."""
        labeled_tokens = []

        # Tokenize the message
        tokens = self.tokenize_message(message)

        # Reset entity flags for each new message
        self.inside_product = False
        self.inside_location = False
        self.inside_price = False

        # Label each token
        for token in tokens:
            labeled_token = self.label_token(token)
            labeled_tokens.append(labeled_token)

        return "\n".join(labeled_tokens)

    def process_messages(self, messages):
        """Processes a list of messages and returns them in CoNLL format."""
        labeled_messages = []
        for message in messages:
            labeled_message = self.label_message(message)
            labeled_messages.append(labeled_message)

        # Combine all labeled messages into one CoNLL formatted string
        return "\n\n".join(labeled_messages)
    def save_to_txt(self, labeled_messages, file_path):
        """Saves the labeled messages to a text file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(labeled_messages)