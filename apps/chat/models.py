# No model here on purpose. Conversation history lives in the visitor's
# session (ephemeral, expires with it) rather than the database — unlike
# contact form submissions, there's no reason to keep a permanent record
# of chat transcripts, and not doing so is one less thing to think about
# regarding visitor data retention.
