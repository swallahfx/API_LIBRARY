// Initialize AI Library Database
print('Starting AI Library database initialization...');

db = db.getSiblingDB('ai_library');

// Create collections with validation
db.createCollection('documents', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["filename", "content_type", "upload_date", "status"],
            properties: {
                filename: { bsonType: "string" },
                content_type: { bsonType: "string" },
                upload_date: { bsonType: "date" },
                status: { 
                    bsonType: "string",
                    enum: ["uploading", "processing", "processed", "failed"]
                },
                chunk_count: { bsonType: "int" },
                file_size: { bsonType: "int" },
                metadata: { bsonType: "object" }
            }
        }
    }
});

db.createCollection('queries', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["question", "answer", "timestamp"],
            properties: {
                question: { bsonType: "string" },
                answer: { bsonType: "string" },
                confidence: { bsonType: "double" },
                timestamp: { bsonType: "date" }
            }
        }
    }
});

db.createCollection('knowledge_base', {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["document_id", "content"],
            properties: {
                document_id: { bsonType: "string" },
                content: { bsonType: "string" },
                metadata: { bsonType: "object" }
            }
        }
    }
});

// Create indexes for better performance
print('Creating database indexes...');

// Documents collection indexes
db.documents.createIndex({ "filename": 1 });
db.documents.createIndex({ "upload_date": -1 });
db.documents.createIndex({ "status": 1 });
db.documents.createIndex({ "content_type": 1 });
db.documents.createIndex({ "metadata.category": 1 });
db.documents.createIndex({ "metadata.tags": 1 });

// Queries collection indexes
db.queries.createIndex({ "timestamp": -1 });
db.queries.createIndex({ "question": "text" });
db.queries.createIndex({ "confidence": -1 });

// Knowledge base indexes
db.knowledge_base.createIndex({ "document_id": 1 });
db.knowledge_base.createIndex({ "content": "text" });
db.knowledge_base.createIndex({ "metadata.chunk_index": 1 });

// Create admin user
db.createUser({
    user: "ai_library_admin",
    pwd: "secure_password_123",
    roles: [
        { role: "readWrite", db: "ai_library" },
        { role: "dbAdmin", db: "ai_library" }
    ]
});

// Insert sample data for testing
print('Inserting sample data...');

db.documents.insertOne({
    "_id": "sample_doc_1",
    "filename": "sample_ai_guide.pdf",
    "content_type": "application/pdf",
    "upload_date": new Date(),
    "status": "processed",
    "chunk_count": 5,
    "file_size": 1024000,
    "metadata": {
        "title": "AI Implementation Guide",
        "author": "Tech Team",
        "category": "Documentation",
        "tags": ["AI", "Machine Learning", "Implementation"]
    }
});

db.knowledge_base.insertMany([
    {
        "_id": "sample_doc_1_chunk_0",
        "document_id": "sample_doc_1",
        "content": "Artificial Intelligence (AI) is transforming how businesses operate...",
        "metadata": {
            "filename": "sample_ai_guide.pdf",
            "chunk_index": 0,
            "page": 1
        }
    },
    {
        "_id": "sample_doc_1_chunk_1",
        "document_id": "sample_doc_1",
        "content": "Machine Learning models require careful training and validation...",
        "metadata": {
            "filename": "sample_ai_guide.pdf",
            "chunk_index": 1,
            "page": 2
        }
    }
]);

print('✅ AI Library database initialized successfully!');
print('📊 Collections created: documents, queries, knowledge_base');
print('🔍 Indexes created for optimal performance');
print('👤 Admin user created: ai_library_admin');
print('📄 Sample data inserted for testing');
