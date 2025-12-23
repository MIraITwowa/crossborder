from django.db import models
from django.conf import settings


class NFTCertificate(models.Model):
    """NFT Certificate for product authenticity"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('MINTING', 'Minting'),
        ('MINTED', 'Minted'),
        ('TRANSFERRED', 'Transferred'),
        ('FAILED', 'Failed'),
    ]
    
    product = models.OneToOneField('products.Product', on_delete=models.CASCADE, related_name='nft_certificate')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='nft_certificates')
    
    # Blockchain data
    contract_address = models.CharField(max_length=255)
    token_id = models.CharField(max_length=100, unique=True)
    blockchain_network = models.CharField(max_length=50, default='ethereum')
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    
    # Certificate metadata
    certificate_data = models.JSONField(default=dict)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    minted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nft_certificates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token_id']),
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"NFT #{self.token_id} - {self.product.name}"


class BlockchainTransaction(models.Model):
    """Track blockchain transactions"""
    
    TRANSACTION_TYPES = [
        ('MINT', 'Mint NFT'),
        ('TRANSFER', 'Transfer Ownership'),
        ('VERIFY', 'Verify Authenticity'),
    ]
    
    nft_certificate = models.ForeignKey(NFTCertificate, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_hash = models.CharField(max_length=255, unique=True)
    from_address = models.CharField(max_length=255, blank=True, null=True)
    to_address = models.CharField(max_length=255, blank=True, null=True)
    gas_used = models.BigIntegerField(null=True, blank=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blockchain_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['nft_certificate', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_hash[:10]}..."
