"""Tests for message module."""

import pytest
from onebot_adapter_client.message import Message, MessageSegment


class TestMessageSegment:
    """Test MessageSegment class."""
    
    def test_text_segment(self):
        """Test text segment creation."""
        segment = MessageSegment.text("Hello, World!")
        assert segment.type == "text"
        assert segment.data["text"] == "Hello, World!"
    
    def test_face_segment(self):
        """Test face segment creation."""
        segment = MessageSegment.face(178)
        assert segment.type == "face"
        assert segment.data["id"] == 178
    
    def test_image_segment(self):
        """Test image segment creation."""
        segment = MessageSegment.image(
            file="test.jpg",
            type="show",
            url="https://example.com/test.jpg"
        )
        assert segment.type == "image"
        assert segment.data["file"] == "test.jpg"
        assert segment.data["type"] == "show"
        assert segment.data["url"] == "https://example.com/test.jpg"
    
    def test_at_segment(self):
        """Test @ segment creation."""
        segment = MessageSegment.at(123456789)
        assert segment.type == "at"
        assert segment.data["qq"] == "123456789"
    
    def test_at_all_segment(self):
        """Test @all segment creation."""
        segment = MessageSegment.at_all()
        assert segment.type == "at"
        assert segment.data["qq"] == "all"
    
    def test_share_segment(self):
        """Test share segment creation."""
        segment = MessageSegment.share(
            url="https://example.com",
            title="Example",
            content="Check this out!"
        )
        assert segment.type == "share"
        assert segment.data["url"] == "https://example.com"
        assert segment.data["title"] == "Example"
        assert segment.data["content"] == "Check this out!"


class TestMessage:
    """Test Message class."""
    
    def test_message_from_string(self):
        """Test creating message from string."""
        message = Message("Hello, World!")
        assert len(message) == 1
        assert message[0].type == "text"
        assert message[0].data["text"] == "Hello, World!"
    
    def test_message_from_segments(self):
        """Test creating message from segments."""
        segments = [
            MessageSegment.text("Hello "),
            MessageSegment.at(123456789),
            MessageSegment.text("!")
        ]
        message = Message(segments)
        assert len(message) == 3
        assert message[0].type == "text"
        assert message[1].type == "at"
        assert message[2].type == "text"
    
    def test_message_from_dicts(self):
        """Test creating message from dictionaries."""
        dicts = [
            {"type": "text", "data": {"text": "Hello"}},
            {"type": "at", "data": {"qq": "123456789"}}
        ]
        message = Message(dicts)
        assert len(message) == 2
        assert message[0].type == "text"
        assert message[1].type == "at"
    
    def test_message_operations(self):
        """Test message operations."""
        message = Message("Hello")
        
        # Append
        message.append(MessageSegment.face(178))
        assert len(message) == 2
        
        # Extend
        message.extend([MessageSegment.text(" World!")])
        assert len(message) == 3
        
        # Insert
        message.insert(1, MessageSegment.at(123456789))
        assert len(message) == 4
        assert message[1].type == "at"
        
        # Remove
        message.remove(message[1])
        assert len(message) == 3
        
        # Pop
        last_segment = message.pop()
        assert last_segment.type == "text"
        assert len(message) == 2
    
    def test_extract_plain_text(self):
        """Test extracting plain text from message."""
        message = Message([
            MessageSegment.text("Hello "),
            MessageSegment.at(123456789),
            MessageSegment.text("! How are you?")
        ])
        
        plain_text = message.extract_plain_text()
        assert plain_text == "Hello ! How are you?"
    
    def test_get_segments_by_type(self):
        """Test getting segments by type."""
        message = Message([
            MessageSegment.text("Hello "),
            MessageSegment.at(123456789),
            MessageSegment.face(178),
            MessageSegment.text("!")
        ])
        
        text_segments = message.get_segments("text")
        assert len(text_segments) == 2
        
        at_segments = message.get_segments("at")
        assert len(at_segments) == 1
        
        face_segments = message.get_segments("face")
        assert len(face_segments) == 1
    
    def test_has_segment(self):
        """Test checking if message has segment of specific type."""
        message_with_at = Message([
            MessageSegment.text("Hello "),
            MessageSegment.at(123456789)
        ])
        assert message_with_at.has_segment("at") is True
        assert message_with_at.has_segment("image") is False
        
        message_without_at = Message([
            MessageSegment.text("Hello "),
            MessageSegment.face(178)
        ])
        assert message_without_at.has_segment("at") is False
    
    def test_is_text_only(self):
        """Test checking if message contains only text segments."""
        text_only_message = Message([
            MessageSegment.text("Hello "),
            MessageSegment.text("World!")
        ])
        assert text_only_message.is_text_only() is True
        
        mixed_message = Message([
            MessageSegment.text("Hello "),
            MessageSegment.face(178)
        ])
        assert mixed_message.is_text_only() is False
    
    def test_to_dict(self):
        """Test converting message to dictionary."""
        message = Message([
            MessageSegment.text("Hello"),
            MessageSegment.at(123456789)
        ])
        
        dict_data = message.to_dict()
        assert len(dict_data) == 2
        assert dict_data[0]["type"] == "text"
        assert dict_data[1]["type"] == "at"
    
    def test_from_dict(self):
        """Test creating message from dictionary."""
        dict_data = [
            {"type": "text", "data": {"text": "Hello"}},
            {"type": "at", "data": {"qq": "123456789"}}
        ]
        
        message = Message.from_dict(dict_data)
        assert len(message) == 2
        assert message[0].type == "text"
        assert message[1].type == "at"
    
    def test_from_str(self):
        """Test creating message from string."""
        message = Message.from_str("Hello, World!")
        assert len(message) == 1
        assert message[0].type == "text"
        assert message[0].data["text"] == "Hello, World!"
    
    def test_str_conversion(self):
        """Test string conversion."""
        message = Message([
            MessageSegment.text("Hello "),
            MessageSegment.at(123456789),
            MessageSegment.text("!")
        ])
        
        str_result = str(message)
        assert str_result == "Hello !"
    
    def test_length(self):
        """Test message length."""
        message = Message([
            MessageSegment.text("Hello"),
            MessageSegment.face(178),
            MessageSegment.text(" World!")
        ])
        assert len(message) == 3
    
    def test_contains(self):
        """Test contains operator."""
        message = Message("Hello, World!")
        assert "Hello" in message
        assert "World" in message
        assert "Missing" not in message
    
    def test_clear(self):
        """Test clearing message."""
        message = Message([
            MessageSegment.text("Hello"),
            MessageSegment.face(178)
        ])
        assert len(message) == 2
        
        message.clear()
        assert len(message) == 0
    
    def test_index_and_count(self):
        """Test index and count methods."""
        text_segment = MessageSegment.text("Hello")
        face_segment = MessageSegment.face(178)
        
        message = Message([text_segment, face_segment, text_segment])
        
        assert message.index(text_segment) == 0
        assert message.index(face_segment) == 1
        
        assert message.count(text_segment) == 2
        assert message.count(face_segment) == 1