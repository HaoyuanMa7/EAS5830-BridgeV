// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
	mapping( address => bool) public approved;
	address[] public tokens;

	event Deposit( address indexed token, address indexed recipient, uint256 amount );
	event Withdrawal( address indexed token, address indexed recipient, uint256 amount );
	event Registration( address indexed token );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);

    }

	function deposit(address _token, address _recipient, uint256 _amount ) public {
		// Check if the token has been registered
		require(approved[_token], "Token not registered");
		
		// Use transferFrom to pull tokens from sender to this contract
		require(ERC20(_token).transferFrom(msg.sender, address(this), _amount), "Transfer failed");
		
		// Emit Deposit event
		emit Deposit(_token, _recipient, _amount);
	}

	function withdraw(address _token, address _recipient, uint256 _amount ) onlyRole(WARDEN_ROLE) public {
		// Transfer tokens from this contract to the recipient
		require(ERC20(_token).transfer(_recipient, _amount), "Transfer failed");
		
		// Emit Withdrawal event
		emit Withdrawal(_token, _recipient, _amount);
	}

	function registerToken(address _token) onlyRole(ADMIN_ROLE) public {
		// Check that the token has not already been registered
		require(!approved[_token], "Token already registered");
		
		// Add the token to the approved mapping
		approved[_token] = true;
		
		// Add the token to the tokens array
		tokens.push(_token);
		
		// Emit Registration event
		emit Registration(_token);
	}


}


