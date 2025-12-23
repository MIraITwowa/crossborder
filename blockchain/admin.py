from django.contrib import admin
from .models import NFTCertificate, BlockchainTransaction


@admin.register(NFTCertificate)
class NFTCertificateAdmin(admin.ModelAdmin):
    """Admin configuration for NFTCertificate model"""
    
    list_display = [
        'token_id', 'product', 'owner', 'status', 'blockchain_network', 'minted_at'
    ]
    list_filter = ['status', 'blockchain_network', 'minted_at']
    search_fields = ['token_id', 'contract_address', 'product__name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at', 'minted_at']
    
    fieldsets = (
        ('Product & Owner', {
            'fields': ('product', 'owner')
        }),
        ('Blockchain Data', {
            'fields': ('contract_address', 'token_id', 'blockchain_network', 'transaction_hash')
        }),
        ('Certificate Data', {
            'fields': ('certificate_data', 'ipfs_hash')
        }),
        ('Status', {
            'fields': ('status', 'minted_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    """Admin configuration for BlockchainTransaction model"""
    
    list_display = [
        'transaction_hash', 'nft_certificate', 'transaction_type',
        'status', 'block_number', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['transaction_hash', 'from_address', 'to_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
